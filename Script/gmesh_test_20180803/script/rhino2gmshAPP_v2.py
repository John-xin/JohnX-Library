import rhinoscriptsyntax as rs
import os
import sqlite3 

def app():
    #find the subLayers of "Physical_Setting"
    layerList=[]
    tmp=[]
    layers=rs.LayerNames()
    for layer in layers:
        tmp=(layer.split("::"))
        if tmp[0]=="dummy" and layer!= "dummy":
            layerList.append(layer)
        

    #layerList=layerList[1:10]
    meshSizeList=[]
    for i in range(len(layerList)):
        meshSizeList.append("6")

    rhino2gmsh(layerList,meshSizeList)
    return
#####################################################################################

def rhino2gmsh(layerList,meshSizeList):
	
    meshSizeDict=[]
    for i in range(len(layerList)):
        tmp="meshSize_"+str(i)
        meshSizeDict.append({'layerName':layerList[i],'meshSize':meshSizeList[i],'meshSizeName':tmp})
        
    mPtDict=load2GeoDict(layerList)
    mLineDict=buildLineDict(mPtDict)
    mLineLoopDict=buildLineLoopDict(mLineDict)
    mSurfDict=buildSurfDict(mLineLoopDict)
    mVolDict=buildVolDict(mSurfDict)
    f= open("test1.geo","w+")
    for i in range(len(layerList)):
        f.write("%s=%s;\n" %(meshSizeDict[i]['meshSizeName'],meshSizeDict[i]['meshSize']))
    
    f.write("\n")
    
    for i in range(len(mPtDict)):
        #rebuild points 
        if mPtDict[i]['isRepeated']==False:
            for j in range(len(meshSizeDict)):
                if mPtDict[i]['layerName']==meshSizeDict[j]['layerName']:
                    ptStr=str(mPtDict[i]['ptX'])+','+str(mPtDict[i]['ptY'])+','+str(mPtDict[i]['ptZ'])
                    f.write("Point(%d)={%s,%s}; //ptDictNo is %d\n" %(mPtDict[i]['ptIndex'],ptStr,meshSizeDict[j]['meshSizeName'],mPtDict[i]['ptDictNo']))
                #end if
            #end for
        #end if
    #end for
    for i in range(len(mLineDict)):
        if mLineDict[i]['isRepeated']==False:
            f.write("Line(%d)={%s,%s};\n" %(mLineDict[i]['lineIndex'],mLineDict[i]['ptIndexList'][0],mLineDict[i]['ptIndexList'][1]))
        #end if
    #end for
    
    for i in range(len(mLineLoopDict)):
        if mLineLoopDict[i]['isRepeated']==False:
            lineIndexListStr=""
            for j in range(len(mLineLoopDict[i]['lineIndexList'])):
                lineIndexListStr+=str(mLineLoopDict[i]['lineIndexList'][j])+','
            
            f.write("Line Loop(%d)={%s};\n" %(mLineLoopDict[i]['lineLoopIndex'],lineIndexListStr[:-1]))
    #end for
    
    for i in range(len(mSurfDict)):
        if mSurfDict[i]['isRepeated']==False:
            lineLoopIndexListStr=""
            for j in range(len(mSurfDict[i]['lineLoopIndexList'])):
                lineLoopIndexListStr+=str(mSurfDict[i]['lineLoopIndexList'][j])+','
            
            f.write("Plane Surface(%d)={%s};\n" %(mSurfDict[i]['surfIndex'],lineLoopIndexListStr[:-1]))
    #end for

    for i in range(len(mVolDict)):
        surfLoopStr=""
        for j in range(len(mVolDict[i]['surfLoopList'])):
            
            surfLoopStr+=str(mVolDict[i]['surfLoopList'][j])+','
        f.write("Surface Loop(%d)={%s};\n" %(mVolDict[i]['volIndex'],surfLoopStr[:-1]))
        f.write("Volume(%d)={%d};\n" %(mVolDict[i]['volIndex'],mVolDict[i]['volIndex']))
    #end for
    
    setPhysical(f)
    setMeshSize(f)
    
    f.close()
    return
    


#####################################################################################

def load2GeoDict(layerList):
    countVolume=0
    countSurface=0
    countLine=0
    countPt=0
    ptDict=[] #define empty list
    ##########################################################################################
    #creat point dict
    #ptDict[i]={ptIndex, ptCoordinate, isRepeated, surfaceMark, volumeMark,layerName}
    for layer in layerList:
        objs=rs.ObjectsByLayer(layer,False) #return polysurfaces id list
        for obj in objs: #each obj stands for a polysurface i.e a volume
            countVolume+=1
            surfaces=rs.ExplodePolysurfaces(obj)
            for surface in surfaces:
                countSurface+=1
                lines=rs.DuplicateSurfaceBorder(surface) #return a closed line
                for line in lines:
                    countLine+=1
                    pts=rs.CurvePoints(line) #return edit points in the line
                    for pt in pts: #ignore the last point as it is same as the first point
                        countPt+=1
                        tmpX=float(pt[0])
                        tmpY=float(pt[1])
                        tmpZ=float(pt[2])
                        tmpX="%.6f" % tmpX
                        tmpY="%.6f" % tmpY
                        tmpZ="%.6f" % tmpZ
                        ptDict.append({'ptIndex':countPt,'ptDictNo':countPt,'ptX':tmpX,'ptY':tmpY,'ptZ':tmpZ,'isRepeated':False,'lineLoopMark':countLine,'surfaceMark':countSurface,'volumeMark':countVolume,'layerName':layer})
                    #end for
                #end for
                rs.DeleteObjects(lines) #delete the duplicate lines
            #end for
            rs.DeleteObjects(surfaces)
        #end for
    #end for

    
    ptDict=dealWithSamePt(ptDict)
    savePtDict2DB(ptDict)
    return ptDict

def dealWithSamePt(ptDict):
    #same point location is assigned with same pointId in ptDict - this is a O(n^2), which can be optimized by balance tree data structure
    #ptDict[1]={ptIndex:1, ptCoordinate:pt, isRepeated, surfaceMark:1, volumeMark:1}
    #if ptDict[5]={ptIndex:5, ptCoordinate:sameAs pt, isRepeated, surfaceMark:1, volumeMark:1} has ptCoordinate same as ptDict[1]
    #transfer2 ptDict[5]={ptIndex:1, ptCoordinate:sameAs pt, isRepeated, surfaceMark:1, volumeMark:1}
    """
    conn=sqlite3.connect('geoDict.db')
    c=conn.cursor()
    for i in c.execute('select * from ptTable'):
        for j in c.execute('select * from ptTable'):
            if i[0]!=j[0] and i[2]==j[2] and i[3]==j[3] and i[4]==j[4] and i[1]>j[1]:
                c.execute('update ptTable set ptIndex=? where ptDictNo=?',(j[1],i[0]))
                c.execute('update ptTable set isRepeated=? where ptDictNo=?',('True',i[0]))
                conn.commit()
        #end for
    #end for
    conn.commit()
    c.close()
    conn.close()
    """
    for i in range(len(ptDict)):
        for j in range(len(ptDict)):
            if i!=j and ptDict[i]['ptX']==ptDict[j]['ptX'] and ptDict[i]['ptY']==ptDict[j]['ptY'] and ptDict[i]['ptZ']==ptDict[j]['ptZ'] and ptDict[i]['ptIndex']!=ptDict[j]['ptIndex']:
                ptDict[j]['ptIndex']=ptDict[i]['ptIndex']
                ptDict[j]['isRepeated']=True
        #end for
    #end for

    return ptDict
    
    
def savePtDict2DB(ptDict):
    conn=sqlite3.connect('geoDict.db')
    c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS ptTable(ptDictNo INTEGER, ptIndex INTEGER, ptX REAL, ptY REAL, ptZ REAL, isRepeated TEXT, lineLoopMark INTEGER, surfaceMark INTEGER, volumeMark INTEGER, layerName TEXT)')
    c.execute('DELETE FROM ptTable')
    for i in range(len(ptDict)):
	entry=(ptDict[i]['ptDictNo'], ptDict[i]['ptIndex'], ptDict[i]['ptX'], ptDict[i]['ptY'], ptDict[i]['ptZ'],
	           ptDict[i]['isRepeated'], ptDict[i]['lineLoopMark'], ptDict[i]['surfaceMark'], ptDict[i]['volumeMark'], ptDict[i]['layerName'])
	c.execute('INSERT INTO ptTable VALUES (?,?,?,?,?,?,?,?,?,?)', entry)
    conn.commit()
    c.close()
    conn.close()
    
    return
	
    
def buildLineDict(ptDict):
    ################################################################################################################
    #create lineDict from ptDict
    #lineDict[i]={lineIndex, lineBy2PtIndex, signedLineIndex, isRepeated, surfaceMark, volumeMark}
    lineDict=[]
    lineIndex=0
    for i in range(1,len(ptDict)):
        if ptDict[i]['volumeMark']==ptDict[i-1]['volumeMark'] and ptDict[i]['surfaceMark']==ptDict[i-1]['surfaceMark'] and ptDict[i]['lineLoopMark']==ptDict[i-1]['lineLoopMark']:#pt in same surface
            lineIndex+=1
            lineDict.append({'lineIndex':lineIndex,'ptIndexList':(ptDict[i-1]['ptIndex'],ptDict[i]['ptIndex']),'signedLineIndex':lineIndex,
            'sPtX':ptDict[i-1]['ptX'],'sPtY':ptDict[i-1]['ptY'],'sPtZ':ptDict[i-1]['ptZ'],'ePtX':ptDict[i]['ptX'],'ePtY':ptDict[i]['ptY'],'ePtZ':ptDict[i]['ptZ'],
            'isRepeated':False,'lineLoopMark':ptDict[i]['lineLoopMark'],'surfaceMark':ptDict[i]['surfaceMark'],'volumeMark':ptDict[i]['volumeMark']})
        #end if
    #end for
    
    #line with same ptIndex problem: 
    #1. assign line with same ptIndex into same lineIndex
    #2. assign lineIndex direction into signLineIndex
    for i in range(len(lineDict)):
        for j in range(len(lineDict)):
            if isSameLine(lineDict[i]['ptIndexList'],lineDict[j]['ptIndexList']) and lineDict[i]['lineIndex']!=lineDict[j]['lineIndex'] and i!=j:
                lineDict[j]['lineIndex']=lineDict[i]['lineIndex']
                if isSameLineDir(lineDict[i]['ptIndexList'],lineDict[j]['ptIndexList']):
                    lineDict[j]['signedLineIndex']=lineDict[i]['signedLineIndex']
                    lineDict[j]['isRepeated']=True
                else:
                    lineDict[j]['signedLineIndex']=-lineDict[i]['signedLineIndex']
                    lineDict[j]['isRepeated']=True
		    
    saveLineDict2DB(lineDict)
    return lineDict
    
def saveLineDict2DB(lineDict):
	conn=sqlite3.connect('geoDict.db')  
        c=conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS lnTable(lnIndex INTEGER, signedLnIndex INTEGER, sPtX REAL, sPtY REAL, sPtZ REAL, ePtX REAL, ePtY REAL, ePtZ REAL, isRepeated TEXT, lineLoopMark INTEGER, surfaceMark INTEGER, volumeMark INTEGER)')
        c.execute('DELETE FROM lnTable')
        for i in range(len(lineDict)):
            entry=(lineDict[i]['lineIndex'],lineDict[i]['signedLineIndex'],lineDict[i]['sPtX'],lineDict[i]['sPtY'],lineDict[i]['sPtZ'],lineDict[i]['ePtX'],lineDict[i]['ePtY'],lineDict[i]['ePtZ'],
            str(lineDict[i]['isRepeated']),lineDict[i]['lineLoopMark'],lineDict[i]['surfaceMark'],lineDict[i]['volumeMark'])
            c.execute('INSERT INTO lnTable VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', entry)
        conn.commit()
        c.close()
        conn.close()	
	return
    
def buildLineLoopDict(lineDict):
    ################################################################################################################
    #create lineLoopDict from lineDict
    lineLoopIndex=0
    lineLoopDict=[]
    lineIndexList=[lineDict[0]['signedLineIndex']]
    for i in range(1,len(lineDict)):
        if lineDict[i]['volumeMark']==lineDict[i-1]['volumeMark'] and lineDict[i]['surfaceMark']==lineDict[i-1]['surfaceMark'] and lineDict[i]['lineLoopMark']==lineDict[i-1]['lineLoopMark']:#pt in same surface
            lineIndexList.append(lineDict[i]['signedLineIndex'])
        elif lineDict[i]['lineLoopMark']!=lineDict[i-1]['lineLoopMark']:
            lineLoopIndex+=1
            lineLoopDict.append({'lineLoopIndex':lineLoopIndex,'lineIndexList':lineIndexList,'isRepeated':False,'surfaceMark':lineDict[i-1]['surfaceMark'],'volumeMark':lineDict[i-1]['volumeMark']})
            lineIndexList=[lineDict[i]['signedLineIndex']]
       #elif lineDict[i]['volumeMark']==lineDict[i-1]['volumeMark'] and lineDict[i]['surfaceMark']!=lineDict[i-1]['surfaceMark'] and lineDict[i]['lineLoopMark']!=lineDict[i-1]['lineLoopMark']:
       #     lineLoopIndex+=1
       #     lineLoopDict.append({'lineLoopIndex':lineLoopIndex,'lineIndexList':lineIndexList,'isRepeated':False,'surfaceMark':lineDict[i-1]['surfaceMark'],'volumeMark':lineDict[i-1]['volumeMark']})
       #     lineIndexList=[lineDict[i]['signedLineIndex']]
        
        if  i == len(lineDict)-1:
            lineLoopIndex+=1
            lineLoopDict.append({'lineLoopIndex':lineLoopIndex,'lineIndexList':lineIndexList,'isRepeated':False,'surfaceMark':lineDict[i]['surfaceMark'],'volumeMark':lineDict[i]['volumeMark']})
    #end for
    
    #same lineLoop problem
    for i in range(len(lineLoopDict)):
        for j in range(len(lineLoopDict)):
            if isSame(lineLoopDict[i]['lineIndexList'],lineLoopDict[j]['lineIndexList']) and lineLoopDict[i]['lineLoopIndex']!=lineLoopDict[j]['lineLoopIndex'] and i!=j:
                lineLoopDict[j]['lineLoopIndex']=lineLoopDict[i]['lineLoopIndex']
                lineLoopDict[j]['isRepeated']=True
    return lineLoopDict
    
def buildSurfDict(lineLoopDict):
    ################################################################################################################
    #create surfDict from lineLoopDict
    #surfDict[i]={surfIndex, lineLoopIndexList, volumeMark}
    surfDict=[]
    surfIndex=0
    lineLoopIndexList=[lineLoopDict[0]['lineLoopIndex']]
    for i in range(1,len(lineLoopDict)):
        if lineLoopDict[i]['volumeMark']==lineLoopDict[i-1]['volumeMark'] and lineLoopDict[i]['surfaceMark']==lineLoopDict[i-1]['surfaceMark']:#pt in same surface
            lineLoopIndexList.append(lineLoopDict[i]['lineLoopIndex'])
        elif lineLoopDict[i]['surfaceMark']!=lineLoopDict[i-1]['surfaceMark']: 
            surfIndex+=1
            surfDict.append({'surfIndex':surfIndex,'lineLoopIndexList':lineLoopIndexList,'isRepeated':False,'volumeMark':lineLoopDict[i-1]['volumeMark']})
            lineLoopIndexList=[lineLoopDict[i]['lineLoopIndex']]
        
        if i==len(lineLoopDict)-1: #last element
            surfIndex+=1
            surfDict.append({'surfIndex':surfIndex,'lineLoopIndexList':lineLoopIndexList,'isRepeated':False,'volumeMark':lineLoopDict[i]['volumeMark']})
            
    #common surface problem: 
    conn=sqlite3.connect('geoDict.db')  
    for i in range(len(surfDict)):
        for j in range(len(surfDict)):
            if isSame(surfDict[i]['lineLoopIndexList'],surfDict[j]['lineLoopIndexList']) and surfDict[i]['surfIndex']!=surfDict[j]['surfIndex'] and i!=j:
                delPtDict2DB(surfDict[j]['surfIndex'],conn)
                surfDict[j]['surfIndex']=surfDict[i]['surfIndex']
                surfDict[j]['isRepeated']=True
    conn.close()            
    return surfDict
    
def delPtDict2DB(surfMarkNum,conn):
        c=conn.cursor()
        x=int(surfMarkNum)
        c.execute('delete * from ptTable where surfaceMark=?',x)
        #c.execute('DELETE FROM ptTable WHERE surfaceMark=?', x)
        conn.commit()
        c.close()	
	return
	
def buildVolDict(surfDict):
    ################################################################################################################
    #create volumeDict from surfDict
    #volumeDict[i]={volIndex, surfLoopList}
    volDict=[]
    volIndex=0
    surfLoopList=[surfDict[0]['surfIndex']]
    for i in range(1,len(surfDict)):
        if surfDict[i]['volumeMark']==surfDict[i-1]['volumeMark']:
            surfLoopList.append(surfDict[i]['surfIndex'])
        elif surfDict[i]['volumeMark']!=surfDict[i-1]['volumeMark']:
            volIndex+=1
            volDict.append({'volIndex':volIndex,'surfLoopList':surfLoopList})
            surfLoopList=[surfDict[i]['surfIndex']]
        
        if i==len(surfDict)-1:#last element
            volIndex+=1
            volDict.append({'volIndex':volIndex,'surfLoopList':surfLoopList})
    return volDict

#####################################################################################


def setPhysical(f):
    conn=sqlite3.connect('geoDict.db')
    #find the subLayers of "Physical_Setting"
    layerList=[]
    tmp=[]
    layers=rs.LayerNames()
    for layer in layers:
        tmp=(layer.split("::"))
        if tmp[0]=="Physical_Setting" and layer!= "Physical_Setting":
            layerList.append(layer)

    for layer in layerList: #each layer is defined as a physical surface
       if rs.IsLayerOn(layer):
            tmp=layer.split("::")
            physicalSurfName=tmp[1]
            surfaceIndexList=[]
            objs=rs.ObjectsByLayer(layer,False) #return surfaces id list
            for obj in objs:
                points=getPtsBySurf(obj)
                surfaceIndex=findSurfIndexByPts(points, conn)
                surfaceIndexList.append(surfaceIndex)
            if objs:
                tmp=str(surfaceIndexList)[1:-1] #ignore first and last
                f.write("Physical Surface(\"%s\")={%s};\n" %(physicalSurfName,tmp))
    
    #write physical volume
    c=conn.cursor()
    volumeMarkList=c.execute('select distinct volumeMark from ptTable')
    volumeIndexList=[]
    for x in volumeMarkList:
        volumeIndexList.append(x[0])
    tmpp=str(volumeIndexList)[1:-1]
    f.write("Physical Volume(\"domain\")={%s};\n" %tmpp)
    conn.commit()
    c.close()
    conn.close()
    return

def setMeshSize(f):
    conn=sqlite3.connect('geoDict.db')
    #find the subLayers of "Mesh_Size_Setting"
    layerList=[]
    tmp=[]
    layers=rs.LayerNames()
    for layer in layers:
        tmp=(layer.split("::"))
        if tmp[0]=="Mesh_Size_Setting" and layer!= "Mesh_Size_Setting":
            layerList.append(layer)

    for layer in layerList: #each sub layer
        if rs.IsLayerOn(layer):
            tmp=layer.split("::")
            tmp2=tmp[1].split("_")
            transfiniteType=tmp2[1]
            transfiniteNo=tmp2[3]
            lineIndexList=[]
            surfaceIndexList=[]
            if transfiniteType=="Line":
                objs=rs.ObjectsByLayer(layer,False)# get all lines
                for obj in objs:
                    points=getPtsByLine(obj)
                    lineIndex=findLineIndexByPts(points, conn)
                    lineIndexList.append(lineIndex)
                if objs:
                    tmp=str(lineIndexList)[1:-1] #ignore first and last
                    f.write("Transfinite Line{%s}=%s;\n" %(tmp,transfiniteNo))
            else:
                objs=rs.ObjectsByLayer(layer,False) #return surfaces id list
                for obj in objs:
                    points=getPtsBySurf(obj)
                    surfaceIndex=findSurfIndexByPts(points, conn)
                    surfaceIndexList.append(surfaceIndex)
                if objs:
                    tmp=str(surfaceIndexList)[1:-1] #ignore first and last
                    f.write("Transfinite Surface{%s};\n" %tmp)
                    f.write("Recombine Surface{%s};\n" %tmp)
    
    conn.close()
    return
    
def getPtsBySurf(surf):
    ptList=[]
    lines=rs.DuplicateSurfaceBorder(surf) #return a closed line
    for line in lines:
        pts=rs.CurvePoints(line) #return edit points in the line
        for pt in pts: #ignore last point as it is same as the first point
            tmp=Point(pt[0],pt[1],pt[2])
            ptList.append(tmp.strVal)
        ptList=ptList[:-1]
    rs.DeleteObjects(lines)
    return ptList
    
def getPtsByLine(line):
    ptList=[]
    pts=rs.CurvePoints(line) #return edit points in the line
    for pt in pts: #ignore last point as it is same as the first point
        tmp=Point(pt[0],pt[1],pt[2])
        ptList.append(tmp.strVal)
    return ptList
    
def findSurfIndexByPts(pts, conn):
    indexList=[]
    surfIndex=0
    c=conn.cursor()
    #fetch surfaceMark with same pt coordinate
    for pt in pts:
        index=c.execute('select surfaceMark from ptTable where ptX=? and ptY=? and ptZ=?', (pt[0],pt[1],pt[2]))
        for i in index:
            indexList.append(i[0])
            
    #find surfaceMark with maximum count
    countMax=0
    for x in indexList:
        count=indexList.count(x)
        if count>countMax:
            surfIndex=x
            countMax=count
    
    conn.commit()
    c.close()
    return surfIndex
    
def findLineIndexByPts(pts, conn):
    indexList=[]
    conn=sqlite3.connect('geoDict.db')
    c=conn.cursor()
    #fetch surfaceMark with same pt coordinate

    index=c.execute("select lnIndex from lnTable where (sPtX=? and sPtY=? and sPtZ=? and ePtX=? and ePtY=? and ePtZ=? and isRepeated='False') or (ePtX=? and ePtY=? and ePtZ=? and sPtX=? and sPtY=? and sPtZ=? and isRepeated='False')", 
    (pts[0][0],pts[0][1],pts[0][2],pts[1][0],pts[1][1],pts[1][2],pts[0][0],pts[0][1],pts[0][2],pts[1][0],pts[1][1],pts[1][2]))
    for x in index:
        lineIndex=x[0]
    conn.commit()
    c.close()
    return lineIndex



#####################################################################################

#parameter box is point list containing 8 points in a counter-clockwise order
def offsetBox(box,dist):
    newBox=box
    #point 0
    newBox[0][0]=box[0][0]-dist
    newBox[0][1]=box[0][1]-dist
    newBox[0][2]=box[0][2]
    #point 1
    newBox[1][0]=box[1][0]+dist
    newBox[1][1]=box[1][1]-dist
    newBox[1][2]=box[1][2]
    #point 2
    newBox[2][0]=box[2][0]+dist
    newBox[2][1]=box[2][1]+dist
    newBox[2][2]=box[2][2]
    #point 3
    newBox[3][0]=box[3][0]-dist
    newBox[3][1]=box[3][1]+dist
    newBox[3][2]=box[3][2]
    #point 4
    newBox[4][0]=box[4][0]-dist
    newBox[4][1]=box[4][1]-dist
    newBox[4][2]=box[4][2]+dist
    #point 5
    newBox[5][0]=box[5][0]+dist
    newBox[5][1]=box[5][1]-dist
    newBox[5][2]=box[5][2]+dist
    #point 6
    newBox[6][0]=box[6][0]+dist
    newBox[6][1]=box[6][1]+dist
    newBox[6][2]=box[6][2]+dist
    #point 7
    newBox[7][0]=box[7][0]-dist
    newBox[7][1]=box[7][1]+dist
    newBox[7][2]=box[7][2]+dist
    newBoxId=rs.AddBox(newBox)
    return newBoxId
    
def addDummyBox():
    objs1=rs.ObjectsByLayer("Surr",False)
    objs2=rs.ObjectsByLayer("Proj",False)
    objs=objs1+objs2
    myBox=rs.BoundingBox(objs)
    newBoxId=offsetBox(myBox,10)
    rs.ObjectLayer(newBoxId,"dummy")
    return

def isSameLine(ptIndexList1,ptIndexList2):
    res = False
    if ptIndexList1[0]==ptIndexList2[1] and ptIndexList1[1]==ptIndexList2[0]:
        res=True
    elif ptIndexList1[0]==ptIndexList2[0] and ptIndexList1[1]==ptIndexList2[1]:
        res=True
    return res 
    
def isSameLineDir(ptIndexList1,ptIndexList2):
    res = False
    if ptIndexList1[0]==ptIndexList2[1] and ptIndexList1[1]==ptIndexList2[0]:
        res=False
    elif ptIndexList1[0]==ptIndexList2[0] and ptIndexList1[1]==ptIndexList2[1]:
        res=True
    return res 

def isSame(indexList1,indexList2):
    res=False
    mylen1=len(indexList1)
    mylen2=len(indexList2)
    if mylen1!=mylen2:
        return res
    else:
        mylen=mylen1
        myList1=[]
        myList2=[]
        for i in range(mylen):
            myList1.append(abs(indexList1[i]))
        for i in range(mylen):
            myList2.append(abs(indexList2[i]))
        myList1.sort()
        myList2.sort()
        for i in range(mylen):
            if myList1[i]!=myList2[i]:
                return res
    res=True
    return res
 
    

#####################################################################################

class Point:
  x=0
  y=0
  z=0
  strVal=(0,0,0)
  def __init__(self,x,y,z):
    self.x = "%.6f" % x
    self.y = "%.6f" % y
    self.z = "%.6f" % z
    self.strVal=(self.x,self.y,self.z)

  def isEqual(self,point):
    if self.x==point.x and self.y==point.y and self.z==point.z:
        print("equal")
        return True
    else:
        print("not equal")
        return False

    


#####################################################################################

app()

#####################################################################################



#####################################################################################