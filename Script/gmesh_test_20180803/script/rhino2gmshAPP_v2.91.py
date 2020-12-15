import rhinoscriptsyntax as rs
import os
import sqlite3 
import rhinoscript.utility as rhutil

def app():
    """
    #find the subLayers of "Physical_Setting"
    layerList=[]
    tmp=[]
    layers=rs.LayerNames()
    for layer in layers:
        tmp=(layer.split("::"))
        if tmp[0]=="dummy" and layer!= "dummy":
            layerList.append(layer)
    """    

    layerList=["box2"]
    meshSizeList=[]
    for i in range(len(layerList)):
        meshSizeList.append(6)

    rhino2gmsh(layerList,meshSizeList)
    return
#####################################################################################

def rhino2gmsh(layerList,meshSizeList):
	
    meshSizeDict=[]
    for i in range(len(layerList)):
        tmp="meshSize_"+str(i)
        meshSizeDict.append({'layerName':layerList[i],'meshSize':meshSizeList[i],'meshSizeName':tmp})
        
    mPtDict=load2GeoDict(layerList,meshSizeList)
    mLineDict=buildLineDict(mPtDict)
    mLineLoopDict=buildLineLoopDict(mLineDict)
    mSurfDict=buildSurfDict(mLineLoopDict)
    mVolDict=buildVolDict(mSurfDict)
    f= open("test_pointMesh.geo","w+")
    for i in range(len(layerList)):
        f.write("%s=%s;\n" %(meshSizeDict[i]['meshSizeName'],meshSizeDict[i]['meshSize']))
    f.write("\n")
    
    for i in range(len(mPtDict)):
        #rebuild points 
        if mPtDict[i]['isRepeated']==False:
                    ptStr=str(mPtDict[i]['ptX'])+','+str(mPtDict[i]['ptY'])+','+str(mPtDict[i]['ptZ'])
                    f.write("Point(%d)={%s,%d}; //ptDictNo is %d\n" %(mPtDict[i]['ptIndex'],ptStr,mPtDict[i]['meshSize'],mPtDict[i]['ptDictNo']))
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

def load2GeoDict(layerList,meshSizeList):
    countVolume=0
    countSurface=0
    countLine=0
    countPt=0
    ptDict=[] #define empty list
    ##########################################################################################
    #creat point dict
    #ptDict[i]={ptIndex, ptCoordinate, isRepeated, surfaceMark, volumeMark,layerName}
    for i in range(len(layerList)):    
        layer=layerList[i]
        meshSize=meshSizeList[i]
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
                        ptDict.append({'ptIndex':countPt,'ptDictNo':countPt,'ptX':tmpX,'ptY':tmpY,'ptZ':tmpZ,'isRepeated':False,'lineLoopMark':countLine,'surfaceMark':countSurface,'volumeMark':countVolume,'layerName':layer,'meshSize':meshSize})
                    #end for
                #end for
                rs.DeleteObjects(lines) #delete the duplicate lines
            #end for
            rs.DeleteObjects(surfaces)
        #end for
    #end for

    
    ptDict=dealWithSamePt(ptDict)
    savePtDict2DB(ptDict)
    ptDict=setPointSize(ptDict)
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
    c.execute('CREATE TABLE IF NOT EXISTS ptTable(ptDictNo INTEGER, ptIndex INTEGER, ptX REAL, ptY REAL, ptZ REAL, isRepeated TEXT, lineLoopMark INTEGER, surfaceMark INTEGER, volumeMark INTEGER, layerName TEXT, meshSize REAL)')
    c.execute('DELETE FROM ptTable')
    for i in range(len(ptDict)):
	entry=(ptDict[i]['ptDictNo'], ptDict[i]['ptIndex'], ptDict[i]['ptX'], ptDict[i]['ptY'], ptDict[i]['ptZ'],
	           str(ptDict[i]['isRepeated']), ptDict[i]['lineLoopMark'], ptDict[i]['surfaceMark'], ptDict[i]['volumeMark'], 
	           ptDict[i]['layerName'],ptDict[i]['meshSize'])
	c.execute('INSERT INTO ptTable VALUES (?,?,?,?,?,?,?,?,?,?,?)', entry)
    conn.commit()
    c.close()
    conn.close()
    
    return
	
def setPointSize(ptDict):
    conn=sqlite3.connect('geoDict.db')
    c=conn.cursor()
    #find the subLayers of "Mesh_Size_Setting"
    layerList=[]
    tmp=[]
    layers=rs.LayerNames()
    for layer in layers:
        tmp=(layer.split("::"))
        if tmp[0]=="Mesh_Size_Point" and layer!= "Mesh_Size_Point":
            layerList.append(layer)

    for layer in layerList: #each sub layer
        if rs.IsLayerOn(layer):
            tmp=layer.split("::")
            tmp2=tmp[1].split("_")
            ptMeshSize=int(tmp2[3])
            objs=rs.ObjectsByLayer(layer,False)# get all points
            for obj in objs:
                pt=rs.coerce3dpoint(obj)
                tmpX=float(pt[0])
                tmpY=float(pt[1])
                tmpZ=float(pt[2])
                tmpX="%.6f" % tmpX
                tmpY="%.6f" % tmpY
                tmpZ="%.6f" % tmpZ
                c.execute('update ptTable set meshSize=? where ptX=? and ptY=? and ptZ=? and isRepeated=?', (ptMeshSize,tmpX,tmpY,tmpZ,'False'))
                index=c.execute('select ptDictNo from ptTable where ptX=? and ptY=? and ptZ=? and isRepeated=?',(tmpX,tmpY,tmpZ,'False'))
                res=index.fetchall()
                foundPtDictNo=res[0][0]
                ptDict[foundPtDictNo-1].update({'meshSize':ptMeshSize})
    conn.commit()
    c.close()
    conn.close()
    return ptDict
    
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
        c#.execute("delete from ptTable where surfaceMark=1")
        c.execute('DELETE FROM ptTable WHERE surfaceMark={}'.format(x))
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
    
def addDummyBox(layerList,offset):
    objsList=[]
    for layer in layerList:
        objs=rs.ObjectsByLayer(layer,False)
        for obj in objs:
            objsList.append(obj)
    myBox=rs.BoundingBox(objsList)
    newBoxId=offsetBox(myBox,offset)
    return newBoxId

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
 
    
def pre1():
    #receive closed polysurfaces - building and ground
    #return at least 1 closed polysurface or multiply closed polysurfaces
    #put boundary surfaces into Physical_Setting Layer (building, ground and Inner_Interface)
    #put interface surfaces into Transfinite_Surf layer (optional)
    #put edges into Transfinite_Line layer (x2 y2 z2)
    
    #create inner box based on buildings
    layerList=["bldg_1","bldg_2"]
    innerBox=addDummyBox(layerList,10)
    
    newLayer("Gmsh_Inner_Box")
    rs.ObjectLayer(innerBox,"Gmsh_Inner_Box")
    
    #get outer box
    outerBox=rs.ObjectsByLayer("Outer_Box")
    
    #divide box into 17 blocks
    blocks=divideOuterBox(outerBox,innerBox)
    count=0
    for block in blocks:
        count+=1
        layerName="Gmsh_Outer_Box::Block_" + str(count)
        newLayer(layerName)
        rs.ObjectLayer(block,layerName)
    
    #form new inner box with ground as Bottom
    cutter=rs.ObjectsByLayer("ground")
    cutInnerBox=cutSolidBySuface(innerBox, cutter)
    rs.DeleteObjects(innerBox)
    rs.ObjectLayer(cutInnerBox,"Gmsh_Inner_Box")
    
    #physical setting - cutInnerBox
    N_cutInnerBox=surfaceFromBox(cutInnerBox, 'N')
    S_cutInnerBox=surfaceFromBox(cutInnerBox, 'S')
    W_cutInnerBox=surfaceFromBox(cutInnerBox, 'W')
    E_cutInnerBox=surfaceFromBox(cutInnerBox, 'E')
    T_cutInnerBox=surfaceFromBox(cutInnerBox, 'T')
    B_cutInnerBox=surfaceFromBox(cutInnerBox, 'B')
    interface_cutInnerBox=[N_cutInnerBox,S_cutInnerBox,W_cutInnerBox,E_cutInnerBox,T_cutInnerBox]
    
    newLayer("Gmsh_Physical::Inner_Interface")
    rs.ObjectLayer(interface_cutInnerBox,"Gmsh_Physical::Inner_Interface")
    newLayer("Gmsh_Physical::Inner_Ground")
    rs.ObjectLayer(B_cutInnerBox,"Gmsh_Physical::Inner_Ground")
    
    
    #boolean difference - remove building from inner box
    for layer in layerList:
        objs=rs.ObjectsByLayer(layer)
        for obj in objs:
            cpObj=rs.CopyObject(obj)
            cutInnerBox=rs.BooleanDifference(cutInnerBox, cpObj )
    finalInnerBox=cutInnerBox
    rs.ObjectLayer(finalInnerBox,"Gmsh_Inner_Box")
    
    #form new blocks with ground as Bottom - Block1 to Block8
    for i in range(8):
        layerName="Gmsh_Outer_Box::Block_" + str(i+1)
        cutBlock=cutSolidBySuface(blocks[i], cutter)
        rs.DeleteObjects(blocks[i])
        rs.ObjectLayer(cutBlock,layerName)
        
    #physical setting - blocks
    cutBlocks=[]
    for i in range(17):
        layerName="Gmsh_Outer_Box::Block_" + str(i+1)
        cutBlock=rs.ObjectsByLayer(layerName)
        cutBlocks.append(cutBlock)
   
    N_outerBox=[]
    S_outerBox=[]
    W_outerBox=[]
    E_outerBox=[]
    T_outerBox=[]
    B_outerBox=[]
    interface_outerBox=[]
        
    N_cutBlock_6=surfaceFromBox(cutBlocks[5], 'N')
    N_cutBlock_7=surfaceFromBox(cutBlocks[6], 'N')
    N_cutBlock_8=surfaceFromBox(cutBlocks[7], 'N')
    N_cutBlock_14=surfaceFromBox(cutBlocks[13], 'N')
    N_cutBlock_15=surfaceFromBox(cutBlocks[14], 'N')
    N_cutBlock_16=surfaceFromBox(cutBlocks[15], 'N')
    N_outerBox=[N_cutBlock_6,N_cutBlock_7,N_cutBlock_8,N_cutBlock_14,N_cutBlock_15,N_cutBlock_16]
    newLayer("Gmsh_Physical::N")
    rs.ObjectLayer(N_outerBox,"Gmsh_Physical::N")
    
    S_cutBlock_1=surfaceFromBox(cutBlocks[0], 'S')
    S_cutBlock_2=surfaceFromBox(cutBlocks[1], 'S')
    S_cutBlock_3=surfaceFromBox(cutBlocks[2], 'S')
    S_cutBlock_9=surfaceFromBox(cutBlocks[8], 'S')
    S_cutBlock_10=surfaceFromBox(cutBlocks[9], 'S')
    S_cutBlock_11=surfaceFromBox(cutBlocks[10], 'S')
    S_outerBox=[S_cutBlock_1,S_cutBlock_2,S_cutBlock_3,S_cutBlock_9,S_cutBlock_10,S_cutBlock_11]
    newLayer("Gmsh_Physical::S")
    rs.ObjectLayer(S_outerBox,"Gmsh_Physical::S")
    
    W_cutBlock_9=surfaceFromBox(cutBlocks[8], 'W')
    W_cutBlock_12=surfaceFromBox(cutBlocks[11], 'W')
    W_cutBlock_14=surfaceFromBox(cutBlocks[13], 'W')
    W_cutBlock_1=surfaceFromBox(cutBlocks[0], 'W')
    W_cutBlock_4=surfaceFromBox(cutBlocks[3], 'W')
    W_cutBlock_6=surfaceFromBox(cutBlocks[5], 'W')
    W_outerBox=[W_cutBlock_9,W_cutBlock_12,W_cutBlock_14,W_cutBlock_1,W_cutBlock_4,W_cutBlock_6]
    newLayer("Gmsh_Physical::W")
    rs.ObjectLayer(W_outerBox,"Gmsh_Physical::W")
    
    E_cutBlock_3=surfaceFromBox(cutBlocks[2], 'E')
    E_cutBlock_5=surfaceFromBox(cutBlocks[4], 'E')
    E_cutBlock_8=surfaceFromBox(cutBlocks[7], 'E')
    E_cutBlock_11=surfaceFromBox(cutBlocks[10], 'E')
    E_cutBlock_13=surfaceFromBox(cutBlocks[12], 'E')
    E_cutBlock_16=surfaceFromBox(cutBlocks[15], 'E')
    E_outerBox=[E_cutBlock_3,E_cutBlock_5,E_cutBlock_8,E_cutBlock_11,E_cutBlock_13,E_cutBlock_16]
    newLayer("Gmsh_Physical::E")
    rs.ObjectLayer(E_outerBox,"Gmsh_Physical::E")
    
    T_cutBlock_9=surfaceFromBox(cutBlocks[8], 'T')
    T_cutBlock_10=surfaceFromBox(cutBlocks[9], 'T')
    T_cutBlock_11=surfaceFromBox(cutBlocks[10], 'T')
    T_cutBlock_12=surfaceFromBox(cutBlocks[11], 'T')
    T_cutBlock_13=surfaceFromBox(cutBlocks[12], 'T')
    T_cutBlock_14=surfaceFromBox(cutBlocks[13], 'T')
    T_cutBlock_15=surfaceFromBox(cutBlocks[14], 'T')
    T_cutBlock_16=surfaceFromBox(cutBlocks[15], 'T')
    T_cutBlock_17=surfaceFromBox(cutBlocks[16], 'T')
    T_outerBox=[T_cutBlock_9,T_cutBlock_10,T_cutBlock_11,T_cutBlock_12,T_cutBlock_13,T_cutBlock_14,T_cutBlock_15,T_cutBlock_16,T_cutBlock_17]
    newLayer("Gmsh_Physical::T")
    rs.ObjectLayer(T_outerBox,"Gmsh_Physical::T")
    
    B_cutBlock_1=surfaceFromBox(cutBlocks[0], 'B')
    B_cutBlock_2=surfaceFromBox(cutBlocks[1], 'B')
    B_cutBlock_3=surfaceFromBox(cutBlocks[2], 'B')
    B_cutBlock_4=surfaceFromBox(cutBlocks[3], 'B')
    B_cutBlock_5=surfaceFromBox(cutBlocks[4], 'B')
    B_cutBlock_6=surfaceFromBox(cutBlocks[5], 'B')
    B_cutBlock_7=surfaceFromBox(cutBlocks[6], 'B')
    B_cutBlock_8=surfaceFromBox(cutBlocks[7], 'B')
    B_outerBox=[B_cutBlock_1,B_cutBlock_2,B_cutBlock_3,B_cutBlock_4,B_cutBlock_5,B_cutBlock_6,B_cutBlock_7,B_cutBlock_8]
    newLayer("Gmsh_Physical::B")
    rs.ObjectLayer(B_outerBox,"Gmsh_Physical::B")
    
    interface_outerBox=rs.CopyObjects(interface_cutInnerBox)
    newLayer("Gmsh_Physical::Outer_Interface")
    rs.ObjectLayer(interface_outerBox,"Gmsh_Physical::Outer_Interface")
    return 
    
def pre2():
    #physical setting
    
    #mesh size setting
    return
    
def outerBox():
    #return 17 closed polysurfaces 
    #put boundary surfaces into Physical_Setting Layer (N,S,E,W,T,B,Outer_Interface) and Transfinite_Surf layer
    #put interface surfaces into Transfinite_Surf layer
    #put edges into Transfinite_Line layer (x1 x2 y1 y2 z1 z2)
    
    
    return
#####################################################################################
def cutSolidBySuface(solid, surf):
    splitSolids=rs.SplitBrep ( solid, surf )
    res=upperPart(splitSolids[0], splitSolids[1])
    upper=res[0]
    rs.DeleteObjects(res[1])

    #solid cut surf
    splitSurfs=rs.SplitBrep ( surf, solid )
    res=innerPart(splitSurfs[0],splitSurfs[1])
    inner=res[0]
    rs.DeleteObjects(res[1])
    #form new solid
    objId=[upper,inner]
    newSolid=rs.JoinSurfaces(objId)
    rs.DeleteObjects(objId)
    return newSolid
    
def innerPart(splitSurf0,splitSurf1):
    if rs.Area(splitSurf0)>rs.Area(splitSurf1):
        return splitSurf1,splitSurf0
    else:
        return splitSurf0,splitSurf1
    
def upperPart(splitSolid0, splitSolid1):
    brep0 = rhutil.coercebrep(splitSolid0, True)
    brep1 = rhutil.coercebrep(splitSolid1, True)
    
    verticeList1=brep0.Vertices
    verticeList2=brep1.Vertices
    try:
        with sqlite3.connect('geoDict.db') as conn:
            conn.execute("DROP TABLE IF EXISTS tmpPtTable")
            sql = """
                 CREATE TABLE IF NOT EXISTS tmpPtTable
               (ptX REAL,
                ptY REAL,
                ptZ REAL,
                partName TEXT)
            """
            conn.execute(sql)
            for vertex in verticeList1:
                entry=(vertex.Location.X, vertex.Location.Y, vertex.Location.Z, 'splitSolid0')
                conn.execute("INSERT INTO tmpPtTable VALUES ( ?, ?, ?, ? )",entry)
            for vertex in verticeList2:
                entry=(vertex.Location.X, vertex.Location.Y, vertex.Location.Z, "splitSolid1")
                conn.execute("INSERT INTO tmpPtTable VALUES ( ?, ?, ?, ? )",entry)
            conn.commit()
            sql="""
                select * from tmpPtTable Order by ptZ DESC
            """
            res=conn.execute(sql)
            for i in res:
                max=i[3]
                break
    except sqlite3.Error as e:
        print("sqlite3 Error:", e)
        
    if max=="splitSolid0":
        return splitSolid0,splitSolid1
    else:
        return splitSolid1,splitSolid0
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
def surfaceFromBox(box, dir='N'):
    surfaces=rs.ExplodePolysurfaces(box)
    vectorList=[]
    for surface in surfaces:
        #brep = rhutil.coercebrep(surface, True)
        point = rs.SurfacePoints(surface)
        param = rs.SurfaceClosestPoint(surface, point[0])
        normal = rs.SurfaceNormal(surface, param)
        normal=(normal.X,normal.Y,normal.Z)

        if normal==(0,-1,0):
            myDir='S'
        elif normal==(0,1,0):
            myDir='N'
        elif normal==(1,0,0):
            myDir='E'
        elif normal==(-1,0,0):
            myDir='W'
        elif normal==(0,0,-1):
            myDir='B'
        else:
            myDir='T'
        if myDir==dir:
            newSurface=rs.CopyObject(surface)
            rs.DeleteObjects(surfaces)
            return newSurface
        

#####################################################################################
def booleanDiff(masterSolid, slaveSolids):
    rs.BooleanDifference
    
    return
    
def lineFromBox(box, dim='x'):
    brep = rhutil.coercebrep(box, True)
    lineX=[]
    lineY=[]
    lineZ=[]
    for edge in brep.Edges:
        start=(edge.PointAtStart.X,edge.PointAtStart.Y,edge.PointAtStart.Z)
        end=(edge.PointAtEnd.X,edge.PointAtEnd.Y,edge.PointAtEnd.Z)
        myLine=rs.AddLine(start, end)
        if edge.PointAtStart.Y==edge.PointAtEnd.Y and edge.PointAtStart.Z==edge.PointAtEnd.Z:
            lineX.append(myLine)
        elif edge.PointAtStart.X==edge.PointAtEnd.X and edge.PointAtStart.Z==edge.PointAtEnd.Z:
            lineY.append(myLine)
        elif edge.PointAtStart.X==edge.PointAtEnd.X and edge.PointAtStart.Y==edge.PointAtEnd.Y:
            lineZ.append(myLine)
    if dim=='x':
        rs.DeleteObjects(lineY)
        rs.DeleteObjects(lineZ)
        return lineX
    elif dim=='y':
        rs.DeleteObjects(lineX)
        rs.DeleteObjects(lineZ)
        return lineY
    elif dim=='z':
        rs.DeleteObjects(lineX)
        rs.DeleteObjects(lineY)
        return lineZ

#####################################################################################
def divideOuterBox(outerBox,innerBox):
    outerBox_p0=ptFromBox(outerBox,'0')
    outerBox_p1=ptFromBox(outerBox,'1')
    outerBox_p2=ptFromBox(outerBox,'2')
    outerBox_p3=ptFromBox(outerBox,'3')
    
    innerBox_p4=ptFromBox(innerBox,'4')
    innerBox_p5=ptFromBox(innerBox,'5')
    innerBox_p6=ptFromBox(innerBox,'6')
    innerBox_p7=ptFromBox(innerBox,'7')
    
    block1=createBoxBy2Pts(outerBox_p0, innerBox_p4)
    block3=createBoxBy2Pts(outerBox_p1, innerBox_p5)
    block8=createBoxBy2Pts(outerBox_p2, innerBox_p6)
    block6=createBoxBy2Pts(outerBox_p3, innerBox_p7)
    
    block1_p1=ptFromBox(block1,'1')
    block2=createBoxBy2Pts(block1_p1, innerBox_p5)
    
    block3_p2=ptFromBox(block3,'2')
    block5=createBoxBy2Pts(block3_p2, innerBox_p6)
    
    block8_p3=ptFromBox(block8,'3')
    block7=createBoxBy2Pts(block8_p3, innerBox_p7)
    
    block1_p3=ptFromBox(block1,'3')
    block4=createBoxBy2Pts(block1_p3, innerBox_p7)
    
    h=innerBox_p4[2]-outerBox_p0[2]
    vector=[0,0,h]
    outerBox_p4=ptFromBox(outerBox,'4')
    factor=(outerBox_p4[2]-innerBox_p4[2])/h
    
    block9=rs.CopyObject(block1,vector)
    block9=rs.ScaleObject(block9,[0,0,h],[1,1,factor])
    
    block10=rs.CopyObject(block2,vector)
    block10=rs.ScaleObject(block10,[0,0,h],[1,1,factor])
    
    block11=rs.CopyObject(block3,vector)
    block11=rs.ScaleObject(block11,[0,0,h],[1,1,factor])
    
    block13=rs.CopyObject(block5,vector)
    block13=rs.ScaleObject(block13,[0,0,h],[1,1,factor])
    
    block16=rs.CopyObject(block8,vector)
    block16=rs.ScaleObject(block16,[0,0,h],[1,1,factor]) 
    
    block15=rs.CopyObject(block7,vector)
    block15=rs.ScaleObject(block15,[0,0,h],[1,1,factor])
    
    block14=rs.CopyObject(block6,vector)
    block14=rs.ScaleObject(block14,[0,0,h],[1,1,factor])
    
    block12=rs.CopyObject(block4,vector)
    block12=rs.ScaleObject(block12,[0,0,h],[1,1,factor])
    
    block17=rs.CopyObject(innerBox,vector)
    block17=rs.ScaleObject(block17,[0,0,h],[1,1,factor])
    
    blocks=[block1, block2, block3, block4, block5, block6, block7, block8,
            block9, block10, block11, block12, block13, block14, block15, block16, block17]
    return blocks
#####################################################################################
def createBoxBy2Pts(pt1,pt2):
    ptX=[]
    ptY=[]
    ptZ=[]
    
    ptX.append(pt1[0])
    ptY.append(pt1[1])
    ptZ.append(pt1[2])
    
    ptX.append(pt2[0])
    ptY.append(pt2[1])
    ptZ.append(pt2[2])
    
    ptX=sorted(ptX)
    ptY=sorted(ptY)
    ptZ=sorted(ptZ)
    x_min=ptX[0]
    x_max=ptX[-1]
    y_min=ptY[0]
    y_max=ptY[-1]
    z_min=ptZ[0]
    z_max=ptZ[-1]
    
    p0=[x_min,y_min,z_min]
    p1=[x_max,y_min,z_min]
    p2=[x_max,y_max,z_min]
    p3=[x_min,y_max,z_min]
    p4=[x_min,y_min,z_max]
    p5=[x_max,y_min,z_max]
    p6=[x_max,y_max,z_max]
    p7=[x_min,y_max,z_max]
    box=[p0,p1,p2,p3,p4,p5,p6,p7]
    myBox=rs.AddBox(box)
    return myBox
    

def ptFromBox(boxID, ptNum='0'):
    brep = rhutil.coercebrep(boxID, True)
    ptX=[]
    ptY=[]
    ptZ=[]
    
    for vertex in brep.Vertices:
        ptX.append(vertex.Location.X)
        ptY.append(vertex.Location.Y)
        ptZ.append(vertex.Location.Z)
        
    ptX=sorted(ptX)
    ptY=sorted(ptY)
    ptZ=sorted(ptZ)
    x_min=ptX[0]
    x_max=ptX[-1]
    y_min=ptY[0]
    y_max=ptY[-1]
    z_min=ptZ[0]
    z_max=ptZ[-1]
    
    for vertex in brep.Vertices:
        if vertex.Location.X==x_min and vertex.Location.Y==y_min and vertex.Location.Z==z_min:
            myPtNum='0'
        elif vertex.Location.X==x_max and vertex.Location.Y==y_min and vertex.Location.Z==z_min:
            myPtNum='1'
        elif vertex.Location.X==x_max and vertex.Location.Y==y_max and vertex.Location.Z==z_min:
            myPtNum='2'
        elif vertex.Location.X==x_min and vertex.Location.Y==y_max and vertex.Location.Z==z_min:
            myPtNum='3'
        elif vertex.Location.X==x_min and vertex.Location.Y==y_min and vertex.Location.Z==z_max:
            myPtNum='4'
        elif vertex.Location.X==x_max and vertex.Location.Y==y_min and vertex.Location.Z==z_max:
            myPtNum='5'
        elif vertex.Location.X==x_max and vertex.Location.Y==y_max and vertex.Location.Z==z_max:
            myPtNum='6'
        elif vertex.Location.X==x_min and vertex.Location.Y==y_max and vertex.Location.Z==z_max:
            myPtNum='7'
            
        if ptNum==myPtNum:
            pt=[vertex.Location.X,vertex.Location.Y,vertex.Location.Z]
            #rs.AddPoint(pt)
            return pt

def newLayer(layerName):
    if rs.IsLayer(layerName):
        if not rs.IsLayerCurrent(layerName):
            objs=rs.ObjectsByLayer(layerName)
            rs.DeleteObjects(objs)
            rs.DeleteLayer(layerName)
        else:
            print "WARNING : change current layer to others and run again"
    rs.AddLayer(layerName)
    return
#app()
pre1()

#####################################################################################



#####################################################################################