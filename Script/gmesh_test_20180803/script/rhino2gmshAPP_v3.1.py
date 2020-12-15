import rhinoscriptsyntax as rs
import os
import sqlite3 
import rhinoscript.utility as rhutil

def case1():
    bldgLayerList=["case1_bldg"]
    groundLayer="case1_outerBox_ground"
    offsetDist=10
    x1=20
    x2=20
    y1=20
    y2=20
    z1=20
    z2=20
    meshSizeList_outerBox=[x1,x2,y1,y2,z1,z2]
    meshSizeList_innerBox=[x2,y2,z1]
    timesOfMaxHeightList=[20,20,5]
    
    preprocess(bldgLayerList,groundLayer,offsetDist,meshSizeList_innerBox, meshSizeList_outerBox,timesOfMaxHeightList)
    
        #find the subLayers of "Physical_Setting"
    layerList=findSubLayerListByName("Gmsh_Outer_Box")
    meshSizeList=[]
    for i in range(len(layerList)):
        meshSizeList.append(1)
    
    Gmsh_Physical_LayerList=findSubLayerListByName("Gmsh_Physical")
    setLayerListNotVisible(Gmsh_Physical_LayerList,str="InnerBox")
    Gmsh_Transfinite_LayerList=findSubLayerListByName("Gmsh_Transfinite")
    setLayerListNotVisible(Gmsh_Transfinite_LayerList,str="InnerBox")
    rhino2gmsh(layerList,meshSizeList,"Case1_outerBox.geo")
    
    setLayerListVisible(Gmsh_Physical_LayerList,str="InnerBox")
    setLayerListVisible(Gmsh_Transfinite_LayerList,str="InnerBox")
    setLayerListNotVisible(Gmsh_Physical_LayerList,str="OuterBox")
    setLayerListNotVisible(Gmsh_Transfinite_LayerList,str="OuterBox")
    rhino2gmsh(["Gmsh_Inner_Box"],[1],"Case1_innerBox.geo")
    return

def app():

    bldgLayerList=["Surr_L","Surr_M","Surr_S","Project"]
    groundLayer="ground_gmsh"
    offsetDist=30
    x1=10
    x2=60
    y1=20
    y2=40
    z1=20
    z2=20
    meshSizeList_outerBox=[x1,x2,y1,y2,z1,z2]
    meshSizeList_innerBox=[x2,y2,z1]
    timesOfMaxHeightList=[70,70,5]
    
    meshSizeLevelList= preprocess(bldgLayerList,groundLayer,offsetDist,meshSizeList_innerBox, meshSizeList_outerBox,timesOfMaxHeightList)
    
    #find the subLayers of "Physical_Setting"
    layerList=findSubLayerListByName("Gmsh_Outer_Box")
    Gmsh_Physical_LayerList=findSubLayerListByName("Gmsh_Physical")
    Gmsh_Transfinite_LayerList=findSubLayerListByName("Gmsh_Transfinite")
    MeshSizePoint_LayerList=findSubLayerListByName("Mesh_Size_Point")
    setLayerListNotVisible(Gmsh_Physical_LayerList,str="InnerBox")
    setLayerListNotVisible(Gmsh_Transfinite_LayerList,str="InnerBox")
    for meshSizePointLayer in MeshSizePoint_LayerList:
        rs.LayerVisible(meshSizePointLayer,False)
    rhino2gmsh(layerList,meshSizeLevelList,"outerBox.geo")
    
    layerList=findSubLayerListByName("Gmsh_Inner_Box")
    setLayerListVisible(Gmsh_Physical_LayerList,str="InnerBox")
    setLayerListVisible(Gmsh_Transfinite_LayerList,str="InnerBox")
    setLayerListNotVisible(Gmsh_Physical_LayerList,str="OuterBox")
    setLayerListNotVisible(Gmsh_Transfinite_LayerList,str="OuterBox")
    for meshSizePointLayer in MeshSizePoint_LayerList:
        rs.LayerVisible(meshSizePointLayer,True)
    rhino2gmsh(layerList,meshSizeLevelList,"innerBox.geo")
    
    return
#####################################################################################

def rhino2gmsh(layerList,meshSizeLevelList,exportFileName):
	
    meshSizeDict=[]
    for i in range(len(meshSizeLevelList)):
        tmpName="meshSizeLevel_"+str(i)
        meshSizeDict.append({'meshSize':meshSizeLevelList[i],'meshSizeName':tmpName})
        
    mPtDict=load2GeoDict(layerList,meshSizeDict)
    mLineDict=buildLineDict(mPtDict)
    mLineLoopDict=buildLineLoopDict(mLineDict)
    mSurfDict=buildSurfDict(mLineLoopDict)
    mVolDict=buildVolDict(mSurfDict)
    
    f= open(exportFileName,"w+")
    for i in range(len(meshSizeDict)):
        f.write("%s=%s;\n" %(meshSizeDict[i]['meshSizeName'],meshSizeDict[i]['meshSize']))
    f.write("\n")
    
    for i in range(len(mPtDict)):
        #rebuild points 
        if mPtDict[i]['isRepeated']==False:
                    ptStr=str(mPtDict[i]['ptX'])+','+str(mPtDict[i]['ptY'])+','+str(mPtDict[i]['ptZ'])
                    f.write("Point(%d)={%s,%s}; //ptDictNo is %d\n" %(mPtDict[i]['ptIndex'],ptStr,mPtDict[i]['meshSize'],mPtDict[i]['ptDictNo']))
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

def load2GeoDict(layerList,meshSizeDict):
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
                        ptDict.append({'ptIndex':countPt,'ptDictNo':countPt,'ptX':tmpX,'ptY':tmpY,'ptZ':tmpZ,'isRepeated':False,'lineLoopMark':countLine,'surfaceMark':countSurface,'volumeMark':countVolume,'layerName':layer,'meshSize':meshSizeDict[0]["meshSizeName"]})
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
    c.execute('CREATE TABLE IF NOT EXISTS ptTable(ptDictNo INTEGER, ptIndex INTEGER, ptX REAL, ptY REAL, ptZ REAL, isRepeated TEXT, lineLoopMark INTEGER, surfaceMark INTEGER, volumeMark INTEGER, layerName TEXT, meshSize TEXT)')
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
            ptMeshSize="meshSizeLevel_"+str(ptMeshSize)
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
        if tmp[0]=="Gmsh_Physical" and layer!= "Gmsh_Physical":
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
        if tmp[0]=="Gmsh_Transfinite" and layer!= "Gmsh_Transfinite":
            layerList.append(layer)

    for layer in layerList: #each sub layer
        if rs.IsLayerOn(layer):
            tmp=layer.split("::")
            tmp2=tmp[1].split("_")
            transfiniteType=tmp2[1]
            transfiniteDir=tmp2[2]
            transfiniteNo=tmp2[3]
            lineIndexList=[]
            surfaceIndexList=[]
            if transfiniteType=="Line":
                transfiniteGrowthRate=tmp2[4]
                objs=rs.ObjectsByLayer(layer,False)# get all lines
                for obj in objs:
                    points=getPtsByLine(obj)
                    lineIndex=findLineIndexByPts(points, conn) #[0] - index, [1] - sPt, [2] - ePt 
                    
                    if transfiniteDir=="x1neg":
                        if lineIndex[1][0]>lineIndex[2][0]: #neg
                            lineIndexList.append(lineIndex[0])
                        else: #pos
                            lineIndexList.append(-lineIndex[0])
                    elif transfiniteDir=="x1pos":
                        if lineIndex[1][0]>lineIndex[2][0]: #neg
                            lineIndexList.append(-lineIndex[0])
                        else:#pos
                            lineIndexList.append(lineIndex[0])
                    elif transfiniteDir=="y1neg":
                        if lineIndex[1][1]>lineIndex[2][1]: #neg
                            lineIndexList.append(lineIndex[0])
                        else: #pos
                            lineIndexList.append(-lineIndex[0])
                    elif transfiniteDir=="y1pos":
                        if lineIndex[1][1]>lineIndex[2][1]: #neg
                            lineIndexList.append(-lineIndex[0])
                        else: #pos
                            lineIndexList.append(lineIndex[0])
                    elif transfiniteDir=="z2":#need pos
                        if lineIndex[1][2]>lineIndex[2][2]: #neg
                            lineIndexList.append(-lineIndex[0])
                        else: #pos
                            lineIndexList.append(lineIndex[0])
                    else:
                        lineIndexList.append(lineIndex[0])
                if objs:
                    tmp=str(lineIndexList)[1:-1] #ignore first and last
                    f.write("Transfinite Line{%s}=%s Using Progression %s;\n" %(tmp,transfiniteNo,transfiniteGrowthRate))
                    
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

    index=c.execute("select LnIndex,sPtX,sPtY,sPtZ,ePtX,ePtY,ePtZ from lnTable where (sPtX=? and sPtY=? and sPtZ=? and ePtX=? and ePtY=? and ePtZ=? and isRepeated='False') or (ePtX=? and ePtY=? and ePtZ=? and sPtX=? and sPtY=? and sPtZ=? and isRepeated='False')", 
    (pts[0][0],pts[0][1],pts[0][2],pts[1][0],pts[1][1],pts[1][2],pts[0][0],pts[0][1],pts[0][2],pts[1][0],pts[1][1],pts[1][2]))
    for x in index:
        indexList=[x[0],(x[1],x[2],x[3]),(x[4],x[5],x[6])]
        #lineIndex=x[0]
    conn.commit()
    c.close()
    return indexList


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
 
    
def preprocess(bldgLayerList,groundLayer,offsetDist,meshSizeList_innerBox, meshSizeList_outerBox, timesOfMaxHeightList):
    #receive closed polysurfaces - building and ground
    #return at least 1 closed polysurface or multiply closed polysurfaces
    #put boundary surfaces into Physical_Setting Layer (building, ground and Inner_Interface)
    #put interface surfaces into Transfinite_Surf layer (optional)
    #put edges into Transfinite_Line layer (x2 y2 z2)
    
    #create inner box based on buildings
    layerList= bldgLayerList
    innerBox=addDummyBox(layerList,offsetDist)
    
    newLayer("Gmsh_Inner_Box")
    rs.ObjectLayer(innerBox,"Gmsh_Inner_Box")
    
    innerBoxDim=findInnerBoxDim(innerBox)
    innerBoxNumOfCellList=meshSizeList_innerBox
    meshSizeLevelList=getMeshSizeLevel(innerBoxDim,innerBoxNumOfCellList)
    
    #create outer box
    outerBox=createOuterBox(innerBox,bldgLayerList,timesOfMaxHeightList)
    newLayer("Outer_Box")
    rs.ObjectLayer(outerBox,"Outer_Box")
    
    #divide box into 17 blocks
    blocks=divideOuterBox(outerBox,innerBox)
    count=0
    for block in blocks:
        count+=1
        layerName="Gmsh_Outer_Box::Block_" + str(count)
        newLayer(layerName)
        rs.ObjectLayer(block,layerName)
    
    #form new inner box with ground as Bottom -> cutInnerBox
    cutter=rs.ObjectsByLayer(groundLayer)
    cutInnerBox=cutSolidBySuface(innerBox, cutter)
    rs.DeleteObjects(innerBox)
    rs.ObjectLayer(cutInnerBox,"Gmsh_Inner_Box")
    
    #physical setting - cutInnerBox
    physicalInnerbox(cutInnerBox)
    meshSizeInnerBox(cutInnerBox,meshSizeList_innerBox)
    
    #boolean difference - remove building from inner box
    for layer in layerList:
        objs=rs.ObjectsByLayer(layer)
        for obj in objs:
            cpObj=rs.CopyObject(obj)
            cutInnerBox=rs.BooleanDifference(cutInnerBox, cpObj )
    finalInnerBox=cutInnerBox
    rs.ObjectLayer(finalInnerBox,"Gmsh_Inner_Box")
    
    newLayer("Gmsh_Physical::InnerBox_Bldgs")
    physicalInnerBox_Bldgs(finalInnerBox)
    
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
   
    physicalOuterBox(cutBlocks)
    meshSizeOuterBox(cutBlocks,meshSizeList_outerBox)
    return meshSizeLevelList
    
def preprocess2(bldgLayerList,groundLayer,offsetDist,meshSizeList_innerBox, meshSizeList_outerBox, timesOfMaxHeightList):
    #receive closed polysurfaces - building and ground
    #return at least 1 closed polysurface or multiply closed polysurfaces
    #put boundary surfaces into Physical_Setting Layer (building, ground and Inner_Interface)
    #put interface surfaces into Transfinite_Surf layer (optional)
    #put edges into Transfinite_Line layer (x2 y2 z2)
    
    #create inner box based on buildings
    layerList= bldgLayerList
    innerBox=addDummyBox(layerList,offsetDist)
    
    newLayer("Gmsh_Inner_Box")
    rs.ObjectLayer(innerBox,"Gmsh_Inner_Box")
    
    #find dim of innerBox and define meshSize Level
    innerBoxDim=findInnerBoxDim(innerBox)
    innerBoxNumOfCellList=meshSizeList_innerBox
    meshSizeLevelList=getMeshSizeLevel(innerBoxDim,innerBoxNumOfCellList)
    
    #create outer box
    outerBox=createOuterBox(innerBox,bldgLayerList,timesOfMaxHeightList)
    newLayer("Outer_Box")
    rs.ObjectLayer(outerBox,"Outer_Box")
    
    #divide box into 17 blocks
    blocks=divideOuterBox(outerBox,innerBox)
    count=0
    for block in blocks:
        count+=1
        layerName="Gmsh_Outer_Box::Block_" + str(count)
        newLayer(layerName)
        rs.ObjectLayer(block,layerName)
    
    #create innerBox sub-blocks
    (sub_blocks, bldgList)=createSubInnerBox(bldgLayerList,10)
    count=0
    for sub_block in sub_blocks:
        count+=1
        layerName="Gmsh_Inner_Box::Block_" + str(count)
        newLayer(layerName)
        rs.ObjectLayer(sub_block,layerName)
        
    #form new inner box with ground as Bottom -> cutInnerBox
    cutter=rs.ObjectsByLayer(groundLayer)
    cutInnerBox=cutSolidBySuface(innerBox, cutter)
    rs.DeleteObjects(innerBox)
    rs.ObjectLayer(cutInnerBox,"Gmsh_Inner_Box")
    
    #form new innerBox sub-blocks with ground as Bottom -> cut_sub_blocks
    count=0
    cut_Sub_blocks=[]
    for sub_block in sub_blocks:
        count+=1
        cut_sub_block=cutSolidBySuface(sub_block, cutter)
        cut_Sub_blocks.append(cut_sub_block)
        layerName="Gmsh_Inner_Box::Block_" + str(count)
        rs.DeleteObjects(sub_block)
        rs.ObjectLayer(cut_sub_block,layerName)
    
    #physical setting - cutInnerBox
    physicalInnerbox(cutInnerBox) #deal with surface of top, lateral
    #deal with surface of bottom
    cutInnerBox_Bottom=rs.ObjectsByLayer("Gmsh_Physical::InnerBox_Ground")#return a list, just use [0]
    dealSurf=cutInnerBox_Bottom[0]
    for bldg in bldgList:
        cutDealSurf=rs.SplitBrep(dealSurf,bldg)
        rs.DeleteObject(dealSurf)
        cutDealSurf=sortSurfaceByArea(cutDealSurf)
        dealSurf=cutDealSurf[0]
        rs.DeleteObject(cutDealSurf[1])
    
    for cut_sub_block in cut_Sub_blocks:
        cutDealSurf=rs.SplitBrep(dealSurf,cut_sub_block)
        rs.DeleteObject(dealSurf)
        cutDealSurf=sortSurfaceByArea(cutDealSurf)
        dealSurf=cutDealSurf[0]
        rs.ObjectLayer(cutDealSurf[1],"Gmsh_Physical::InnerBox_Ground")
    rs.ObjectLayer(dealSurf,"Gmsh_Physical::InnerBox_Ground")
    
    #meshSize setting - cutInnerBox
    meshSizeInnerBox(cutInnerBox,meshSizeList_innerBox)
    
    #boolean difference - remove building from innerBox_sub_blocks and remove sub_blocks from innerBox
    count=0
    boolean_sub_blocks=[]
    for i in range(len(cut_Sub_blocks)):
        count+=1
        cpBldg=rs.CopyObject(bldgList[i])
        cpSubBlock=rs.CopyObject(cut_Sub_blocks[i])
        boolean_sub_block=rs.BooleanDifference(cpSubBlock, cpBldg )
        boolean_sub_blocks.append(boolean_sub_block[0])
        layerName="Gmsh_Inner_Box::Block_" + str(count)
        rs.ObjectLayer(boolean_sub_block[0],layerName)
        
        cutInnerBox=rs.BooleanDifference(cutInnerBox, cut_Sub_blocks[i])
        
    #rs.BooleanUnion(boolean_sub_blocks)
    
    boolean_innerBox=cutInnerBox
    newLayer("Gmsh_Inner_Box::Block_Main")
    rs.ObjectLayer(boolean_innerBox,"Gmsh_Inner_Box::Block_Main")
    
    #physical setting - bldgs
    newLayer("Gmsh_Physical::InnerBox_Bldgs")
    for boolean_sub_block in boolean_sub_blocks:
        physicalInnerBox_Bldgs(boolean_sub_block)
    
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
   
    physicalOuterBox(cutBlocks)
    
    #meshSize setting - blocks
    meshSizeOuterBox(cutBlocks,meshSizeList_outerBox)
    return meshSizeLevelList
    
def createSubInnerBox(bldgLayerList,offsetDist):
    blockList=[]
    bldgList=[]
    for layer in bldgLayerList:
        objs=rs.ObjectsByLayer(layer)
        for obj in objs:
            bldgList.append(obj)
            myBox=rs.BoundingBox(obj)
            block=offsetBox(myBox,offsetDist)
            blockList.append(block)
    #newBlockList=rs.BooleanUnion(blockList)
    #rs.ObjectLayer(newBlockList,"Layer 01")
    return blockList,bldgList
    
def physicalOuterBox(cutBlocks):
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
    newLayer("Gmsh_Physical::OuterBox_N")
    rs.ObjectLayer(N_outerBox,"Gmsh_Physical::OuterBox_N")
    
    S_cutBlock_1=surfaceFromBox(cutBlocks[0], 'S')
    S_cutBlock_2=surfaceFromBox(cutBlocks[1], 'S')
    S_cutBlock_3=surfaceFromBox(cutBlocks[2], 'S')
    S_cutBlock_9=surfaceFromBox(cutBlocks[8], 'S')
    S_cutBlock_10=surfaceFromBox(cutBlocks[9], 'S')
    S_cutBlock_11=surfaceFromBox(cutBlocks[10], 'S')
    S_outerBox=[S_cutBlock_1,S_cutBlock_2,S_cutBlock_3,S_cutBlock_9,S_cutBlock_10,S_cutBlock_11]
    newLayer("Gmsh_Physical::OuterBox_S")
    rs.ObjectLayer(S_outerBox,"Gmsh_Physical::OuterBox_S")
    
    W_cutBlock_9=surfaceFromBox(cutBlocks[8], 'W')
    W_cutBlock_12=surfaceFromBox(cutBlocks[11], 'W')
    W_cutBlock_14=surfaceFromBox(cutBlocks[13], 'W')
    W_cutBlock_1=surfaceFromBox(cutBlocks[0], 'W')
    W_cutBlock_4=surfaceFromBox(cutBlocks[3], 'W')
    W_cutBlock_6=surfaceFromBox(cutBlocks[5], 'W')
    W_outerBox=[W_cutBlock_9,W_cutBlock_12,W_cutBlock_14,W_cutBlock_1,W_cutBlock_4,W_cutBlock_6]
    newLayer("Gmsh_Physical::OuterBox_W")
    rs.ObjectLayer(W_outerBox,"Gmsh_Physical::OuterBox_W")
    
    E_cutBlock_3=surfaceFromBox(cutBlocks[2], 'E')
    E_cutBlock_5=surfaceFromBox(cutBlocks[4], 'E')
    E_cutBlock_8=surfaceFromBox(cutBlocks[7], 'E')
    E_cutBlock_11=surfaceFromBox(cutBlocks[10], 'E')
    E_cutBlock_13=surfaceFromBox(cutBlocks[12], 'E')
    E_cutBlock_16=surfaceFromBox(cutBlocks[15], 'E')
    E_outerBox=[E_cutBlock_3,E_cutBlock_5,E_cutBlock_8,E_cutBlock_11,E_cutBlock_13,E_cutBlock_16]
    newLayer("Gmsh_Physical::OuterBox_E")
    rs.ObjectLayer(E_outerBox,"Gmsh_Physical::OuterBox_E")
    
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
    newLayer("Gmsh_Physical::OuterBox_T")
    rs.ObjectLayer(T_outerBox,"Gmsh_Physical::OuterBox_T")
    
    B_cutBlock_1=surfaceFromBox(cutBlocks[0], 'B')
    B_cutBlock_2=surfaceFromBox(cutBlocks[1], 'B')
    B_cutBlock_3=surfaceFromBox(cutBlocks[2], 'B')
    B_cutBlock_4=surfaceFromBox(cutBlocks[3], 'B')
    B_cutBlock_5=surfaceFromBox(cutBlocks[4], 'B')
    B_cutBlock_6=surfaceFromBox(cutBlocks[5], 'B')
    B_cutBlock_7=surfaceFromBox(cutBlocks[6], 'B')
    B_cutBlock_8=surfaceFromBox(cutBlocks[7], 'B')
    B_outerBox=[B_cutBlock_1,B_cutBlock_2,B_cutBlock_3,B_cutBlock_4,B_cutBlock_5,B_cutBlock_6,B_cutBlock_7,B_cutBlock_8]
    newLayer("Gmsh_Physical::OuterBox_B")
    rs.ObjectLayer(B_outerBox,"Gmsh_Physical::OuterBox_B")
    
    interface_cutInnerBox=rs.ObjectsByLayer("Gmsh_Physical::InnerBox_Interface")
    interface_outerBox=rs.CopyObjects(interface_cutInnerBox)
    newLayer("Gmsh_Physical::OuterBox_Interface")
    rs.ObjectLayer(interface_outerBox,"Gmsh_Physical::OuterBox_Interface")
    return

def physicalInnerbox(cutInnerBox):
    N_cutInnerBox=surfaceFromBox(cutInnerBox, 'N')
    S_cutInnerBox=surfaceFromBox(cutInnerBox, 'S')
    W_cutInnerBox=surfaceFromBox(cutInnerBox, 'W')
    E_cutInnerBox=surfaceFromBox(cutInnerBox, 'E')
    T_cutInnerBox=surfaceFromBox(cutInnerBox, 'T')
    B_cutInnerBox=surfaceFromBox(cutInnerBox, 'B')
    interface_cutInnerBox=[N_cutInnerBox,S_cutInnerBox,W_cutInnerBox,E_cutInnerBox,T_cutInnerBox]
    newLayer("Gmsh_Physical::InnerBox_Interface")
    rs.ObjectLayer(interface_cutInnerBox,"Gmsh_Physical::InnerBox_Interface")
    newLayer("Gmsh_Physical::InnerBox_Ground")
    rs.ObjectLayer(B_cutInnerBox,"Gmsh_Physical::InnerBox_Ground")
    return
    
def physicalInnerBox_Bldgs(closedPolySurfaces):
    boundBox=rs.BoundingBox(closedPolySurfaces)
    listX=[]
    listY=[]
    listZ=[]
    for i in range(len(boundBox)):
        listX.append(boundBox[i][0])
        listY.append(boundBox[i][1])
        listZ.append(boundBox[i][2])
    sListX=sorted(listX)
    sListY=sorted(listY)
    sListZ=sorted(listZ)
    minX=sListX[0]
    maxX=sListX[-1]
    minY=sListY[0]
    maxY=sListY[-1]
    minZ=sListZ[0]
    maxZ=sListZ[-1]
    surfs=rs.ExplodePolysurfaces(closedPolySurfaces)
    for surf in surfs:
        brepSurf=rhutil.coercebrep(surf, True)
        for vertex in brepSurf.Vertices:
            x=vertex.Location.X
            y=vertex.Location.Y
            z=vertex.Location.Z
            if x>minX and x<maxX and y>minY and y<maxY:
                flag=1
            else:
                flag=0
                break
        if flag:
            bldgSurf=rs.CopyObject(surf)
            rs.ObjectLayer(bldgSurf,"Gmsh_Physical::InnerBox_Bldgs")
    rs.DeleteObjects(surfs)
    return
    
def meshSizeOuterBox(cutBlocks,meshSizeList):
    
    blk1_lines_x=lineFromBox(cutBlocks[0], 'x')
    blk4_lines_x=lineFromBox(cutBlocks[3], 'x')
    blk6_lines_x=lineFromBox(cutBlocks[5], 'x')
    blk9_lines_x=lineFromBox(cutBlocks[8], 'x')
    blk12_lines_x=lineFromBox(cutBlocks[11], 'x')
    blk14_lines_x=lineFromBox(cutBlocks[13], 'x')
    
    blk3_lines_x=lineFromBox(cutBlocks[2], 'x')
    blk5_lines_x=lineFromBox(cutBlocks[4], 'x')
    blk8_lines_x=lineFromBox(cutBlocks[7], 'x')
    blk11_lines_x=lineFromBox(cutBlocks[10], 'x')
    blk13_lines_x=lineFromBox(cutBlocks[12], 'x')
    blk16_lines_x=lineFromBox(cutBlocks[15], 'x')
    
    blk1_lines_y=lineFromBox(cutBlocks[0], 'y')
    blk2_lines_y=lineFromBox(cutBlocks[1], 'y')
    blk3_lines_y=lineFromBox(cutBlocks[2], 'y')
    blk9_lines_y=lineFromBox(cutBlocks[8], 'y')
    blk10_lines_y=lineFromBox(cutBlocks[9], 'y')
    blk11_lines_y=lineFromBox(cutBlocks[10], 'y')
    blk6_lines_y=lineFromBox(cutBlocks[5], 'y')
    blk7_lines_y=lineFromBox(cutBlocks[6], 'y')
    blk8_lines_y=lineFromBox(cutBlocks[7], 'y')
    blk14_lines_y=lineFromBox(cutBlocks[13], 'y')
    blk15_lines_y=lineFromBox(cutBlocks[14], 'y')
    blk16_lines_y=lineFromBox(cutBlocks[15], 'y')
    
    blk1_lines_z=lineFromBox(cutBlocks[0], 'z')
    blk2_lines_z=lineFromBox(cutBlocks[1], 'z')
    blk3_lines_z=lineFromBox(cutBlocks[2], 'z')
    blk4_lines_z=lineFromBox(cutBlocks[3], 'z')
    blk5_lines_z=lineFromBox(cutBlocks[4], 'z')
    blk6_lines_z=lineFromBox(cutBlocks[5], 'z')
    blk7_lines_z=lineFromBox(cutBlocks[6], 'z')
    blk8_lines_z=lineFromBox(cutBlocks[7], 'z')
    
    blk2_lines_x=lineFromBox(cutBlocks[1], 'x')
    blk7_lines_x=lineFromBox(cutBlocks[6], 'x')
    blk10_lines_x=lineFromBox(cutBlocks[9], 'x')
    blk15_lines_x=lineFromBox(cutBlocks[14], 'x')
    blk17_lines_x=lineFromBox(cutBlocks[16], 'x')
    
    blk4_lines_y=lineFromBox(cutBlocks[3], 'y')
    blk5_lines_y=lineFromBox(cutBlocks[4], 'y')
    blk12_lines_y=lineFromBox(cutBlocks[11], 'y')
    blk13_lines_y=lineFromBox(cutBlocks[12], 'y')
    blk17_lines_y=lineFromBox(cutBlocks[16], 'y')
    
    blk9_lines_z=lineFromBox(cutBlocks[8], 'z')
    blk10_lines_z=lineFromBox(cutBlocks[9], 'z')
    blk11_lines_z=lineFromBox(cutBlocks[10], 'z')
    blk12_lines_z=lineFromBox(cutBlocks[11], 'z')
    blk13_lines_z=lineFromBox(cutBlocks[12], 'z')
    blk14_lines_z=lineFromBox(cutBlocks[13], 'z')
    blk15_lines_z=lineFromBox(cutBlocks[14], 'z')
    blk16_lines_z=lineFromBox(cutBlocks[15], 'z')
    blk17_lines_z=lineFromBox(cutBlocks[16], 'z')
    
    x1_MeshSize=meshSizeList[0]
    x2_MeshSize=meshSizeList[1]
    y1_MeshSize=meshSizeList[2]
    y2_MeshSize=meshSizeList[3]
    z1_MeshSize=meshSizeList[4]
    z2_MeshSize=meshSizeList[5]
    x1_growthRate=findGrowthRate(rs.CurveLength(blk1_lines_x[0]),rs.CurveLength(blk2_lines_x[0])/x2_MeshSize,x1_MeshSize)
    y1_growthRate=findGrowthRate(rs.CurveLength(blk1_lines_y[0]),rs.CurveLength(blk4_lines_y[0])/y2_MeshSize,y1_MeshSize)
    z2_growthRate=findGrowthRate(rs.CurveLength(blk9_lines_z[0]),rs.CurveLength(blk2_lines_z[0])/z1_MeshSize,z2_MeshSize)
    
    layer_x1pos="Gmsh_Transfinite::OuterBox_Line_x1pos_"+str(x1_MeshSize)+"_"+str(x1_growthRate)
    layer_x1neg="Gmsh_Transfinite::OuterBox_Line_x1neg_"+str(x1_MeshSize)+"_"+str(x1_growthRate)
    layer_x2="Gmsh_Transfinite::OuterBox_Line_x2_"+str(x2_MeshSize)+"_1.0"
    layer_y1pos="Gmsh_Transfinite::OuterBox_Line_y1pos_"+str(y1_MeshSize)+"_"+str(y1_growthRate)
    layer_y1neg="Gmsh_Transfinite::OuterBox_Line_y1neg_"+str(y1_MeshSize)+"_"+str(y1_growthRate)
    layer_y2="Gmsh_Transfinite::OuterBox_Line_y2_"+str(y2_MeshSize)+"_1.0"
    layer_z1="Gmsh_Transfinite::OuterBox_Line_z1_"+str(z1_MeshSize)+"_1.0"
    layer_z2="Gmsh_Transfinite::OuterBox_Line_z2_"+str(z2_MeshSize)+"_"+str(z2_growthRate)
    newLayer(layer_x1pos)
    newLayer(layer_x1neg)
    newLayer(layer_x2)
    newLayer(layer_y1pos)
    newLayer(layer_y1neg)
    newLayer(layer_y2)
    newLayer(layer_z1)
    newLayer(layer_z2)
    
    rs.ObjectLayer(blk1_lines_x,layer_x1neg)
    rs.ObjectLayer(blk4_lines_x,layer_x1neg)
    rs.ObjectLayer(blk6_lines_x,layer_x1neg)
    rs.ObjectLayer(blk9_lines_x,layer_x1neg)
    rs.ObjectLayer(blk12_lines_x,layer_x1neg)
    rs.ObjectLayer(blk14_lines_x,layer_x1neg)
    rs.ObjectLayer(blk3_lines_x,layer_x1pos)
    rs.ObjectLayer(blk5_lines_x,layer_x1pos)
    rs.ObjectLayer(blk8_lines_x,layer_x1pos)
    rs.ObjectLayer(blk11_lines_x,layer_x1pos)
    rs.ObjectLayer(blk13_lines_x,layer_x1pos)
    rs.ObjectLayer(blk16_lines_x,layer_x1pos)
    
    rs.ObjectLayer(blk1_lines_y,layer_y1neg)
    rs.ObjectLayer(blk2_lines_y,layer_y1neg)
    rs.ObjectLayer(blk3_lines_y,layer_y1neg)
    rs.ObjectLayer(blk9_lines_y,layer_y1neg)
    rs.ObjectLayer(blk10_lines_y,layer_y1neg)
    rs.ObjectLayer(blk11_lines_y,layer_y1neg)
    
    rs.ObjectLayer(blk6_lines_y,layer_y1pos)
    rs.ObjectLayer(blk7_lines_y,layer_y1pos)
    rs.ObjectLayer(blk8_lines_y,layer_y1pos)
    rs.ObjectLayer(blk14_lines_y,layer_y1pos)
    rs.ObjectLayer(blk15_lines_y,layer_y1pos)
    rs.ObjectLayer(blk16_lines_y,layer_y1pos)
    
    rs.ObjectLayer(blk1_lines_z,layer_z1)
    rs.ObjectLayer(blk2_lines_z,layer_z1)
    rs.ObjectLayer(blk3_lines_z,layer_z1)
    rs.ObjectLayer(blk4_lines_z,layer_z1)
    rs.ObjectLayer(blk5_lines_z,layer_z1)
    rs.ObjectLayer(blk6_lines_z,layer_z1)
    rs.ObjectLayer(blk7_lines_z,layer_z1)
    rs.ObjectLayer(blk8_lines_z,layer_z1)
    
    rs.ObjectLayer(blk2_lines_x,layer_x2)
    rs.ObjectLayer(blk7_lines_x,layer_x2)
    rs.ObjectLayer(blk10_lines_x,layer_x2)
    rs.ObjectLayer(blk15_lines_x,layer_x2)
    rs.ObjectLayer(blk17_lines_x,layer_x2)
    
    rs.ObjectLayer(blk4_lines_y,layer_y2)
    rs.ObjectLayer(blk5_lines_y,layer_y2)
    rs.ObjectLayer(blk12_lines_y,layer_y2)
    rs.ObjectLayer(blk13_lines_y,layer_y2)
    rs.ObjectLayer(blk17_lines_y,layer_y2)
    
    rs.ObjectLayer(blk9_lines_z,layer_z2)
    rs.ObjectLayer(blk10_lines_z,layer_z2)
    rs.ObjectLayer(blk11_lines_z,layer_z2)
    rs.ObjectLayer(blk12_lines_z,layer_z2)
    rs.ObjectLayer(blk13_lines_z,layer_z2)
    rs.ObjectLayer(blk14_lines_z,layer_z2)
    rs.ObjectLayer(blk15_lines_z,layer_z2)
    rs.ObjectLayer(blk16_lines_z,layer_z2)
    rs.ObjectLayer(blk17_lines_z,layer_z2)
    
    layer_surface="Gmsh_Transfinite::OuterBox_Surf_No_1"
    newLayer(layer_surface)
    for block in cutBlocks:
        objs=rs.ExplodePolysurfaces(block)
        rs.ObjectLayer(objs,layer_surface)
    return

def meshSizeInnerBox(cutInnerBox,meshSizeList):
    x_MeshSize=meshSizeList[0]
    y_MeshSize=meshSizeList[1]
    z_MeshSize=meshSizeList[2]
    layer_x="Gmsh_Transfinite::InnerBox_Line_x_"+str(x_MeshSize)+"_1.0"
    layer_y="Gmsh_Transfinite::InnerBox_Line_y_"+str(y_MeshSize)+"_1.0"
    layer_z="Gmsh_Transfinite::InnerBox_Line_z_"+str(z_MeshSize)+"_1.0"
    newLayer(layer_x)
    newLayer(layer_y)
    newLayer(layer_z)
    lines_x=lineFromBox(cutInnerBox, 'x')
    lines_y=lineFromBox(cutInnerBox, 'y')
    lines_z=lineFromBox(cutInnerBox, 'z')
    rs.ObjectLayer(lines_x,layer_x)
    rs.ObjectLayer(lines_y,layer_y)
    rs.ObjectLayer(lines_z,layer_z)
    
    N_cutInnerBox=surfaceFromBox(cutInnerBox, 'N')
    S_cutInnerBox=surfaceFromBox(cutInnerBox, 'S')
    W_cutInnerBox=surfaceFromBox(cutInnerBox, 'W')
    E_cutInnerBox=surfaceFromBox(cutInnerBox, 'E')
    T_cutInnerBox=surfaceFromBox(cutInnerBox, 'T')
    layer_surface=[N_cutInnerBox,S_cutInnerBox,W_cutInnerBox,E_cutInnerBox,T_cutInnerBox]
    newLayer("Gmsh_Transfinite::InnerBox_Surf_No_1")
    rs.ObjectLayer(layer_surface,"Gmsh_Transfinite::InnerBox_Surf_No_1")
    return

def sortSurfaceByArea(surfaceList):
    sortList=[]
    for surface in surfaceList:
        area=rs.Area(surface)
        sortList.append([surface,area])
    sortList.sort(key=lambda tup: tup[1], reverse=True)
    for i in range(len(sortList)):
        surfaceList[i]=sortList[i][0]
    return surfaceList
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
        startPtX="%.6f" % edge.PointAtStart.X
        startPtY="%.6f" % edge.PointAtStart.Y
        startPtZ="%.6f" % edge.PointAtStart.Z
        endPtX="%.6f" % edge.PointAtEnd.X
        endPtY="%.6f" % edge.PointAtEnd.Y
        endPtZ="%.6f" % edge.PointAtEnd.Z
        
        if startPtY==endPtY and startPtZ==endPtZ:
            lineX.append(myLine)
        elif startPtX==endPtX and startPtZ==endPtZ:
            lineY.append(myLine)
        elif startPtX==endPtX and startPtY==endPtY:
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

def findSubLayerListByName(layerName):
    layerList=[]
    tmp=[]
    layers=rs.LayerNames()
    for layer in layers:
        tmp=(layer.split("::"))
        if tmp[0]==layerName and layer!= layerName:
            layerList.append(layer)
    return layerList

def setLayerListVisible(layerList,str="InnerBox"):
    
    for layer in layerList:
        tmp=layer.split("::")
        tmp1=tmp[1].split("_")
        if tmp1[0] == str:
            rs.LayerVisible(layer,True)
    return
    
def setLayerListNotVisible(layerList,str="InnerBox"):
    for layer in layerList:
        tmp=layer.split("::")
        tmp1=tmp[1].split("_")
        if tmp1[0] == str:
            rs.LayerVisible(layer,False)
    return
    
###############################################################################################
def createOuterBox(innerBox,bldgLayerList,timesOfMaxHeightList):
    #find centroid of innerBox : (Cx,Cy,0)
    centroid=findBoxCentroid(innerBox)
    #outerBox's Vertices: (Cx-outerBox_length/2,Cy-outerBox_length/2, 0) (Cx+outerBox_length/2,Cy+outerBox_length/2, outerBox_height)
    innerBoxDim=findInnerBoxDim(innerBox)
    maxBldgHeight=findMaxBldgHeight(bldgLayerList)
    outerBoxDim=findOuterBoxDim(maxBldgHeight,innerBoxDim,timesOfMaxHeightList)
    pt1=(centroid[0]-outerBoxDim[0]/2,centroid[1]-outerBoxDim[1]/2, 0)
    pt2=(centroid[0]+outerBoxDim[0]/2,centroid[1]+outerBoxDim[1]/2, outerBoxDim[2])
    #create outerBox based on vertices
    outerBox=createBoxBy2Pts(pt1,pt2)
    return outerBox
    
def findOuterBoxDim(maxBldgHeight,innerBoxDim,timesOfMaxHeightList):
    #outerBoxLength=timesOfMaxHeightList[0]*maxBldgHeight-innerBoxDim[0]
    #outerBoxWidth=timesOfMaxHeightList[1]*maxBldgHeight-innerBoxDim[1]
    #outerBoxHeight=timesOfMaxHeightList[2]*maxBldgHeight-innerBoxDim[2]
    
    outerBoxLength=timesOfMaxHeightList[0]*maxBldgHeight
    outerBoxWidth=timesOfMaxHeightList[1]*maxBldgHeight
    outerBoxHeight=timesOfMaxHeightList[2]*maxBldgHeight
    return (outerBoxLength, outerBoxWidth, outerBoxHeight)
    
def findMaxBldgHeight(bldgLayerList): 
    # input closed bldg with partial topo bottom
    maxBldgHeight=0
    
    for layer in bldgLayerList:
        objs=rs.ObjectsByLayer(layer)
        for obj in objs:
            brep=rhutil.coercebrep(obj, True)
            ptList=[]
            for vertex in brep.Vertices:
                x=vertex.Location.X
                y=vertex.Location.Y
                z=vertex.Location.Z
                ptList.append((x,y,z))
            ptList.sort(key=lambda tup:tup[2])
            h=ptList[-1][2]-ptList[0][2]
            if h > maxBldgHeight:
                maxBldgHeight=h
    return maxBldgHeight
    
def findBoxCentroid(innerBox):
    centroid=rs.SurfaceVolumeCentroid(innerBox)
    pt=(centroid[0].X,centroid[0].Y,centroid[0].Z)
    #rs.AddPoint(pt)
    #print pt
    return pt
    
def findInnerBoxDim(innerBox):
    brep=rhutil.coercebrep(innerBox, True)
    listX=[]
    listY=[]
    listZ=[]
    for vertex in brep.Vertices:
        x=vertex.Location.X
        y=vertex.Location.Y
        z=vertex.Location.Z
        listX.append(x)
        listY.append(y)
        listZ.append(z)
    listX.sort()
    listY.sort()
    listZ.sort()
    innerBoxLength=listX[-1]-listX[0]
    innerBoxWidth=listY[-1]-listY[0]
    innerBoxHeight=listZ[-1]-listZ[0]
    return (innerBoxLength, innerBoxWidth, innerBoxHeight)
    
    
###############################################################################################    
def getMeshSizeLevel(innerBoxDim,innerBoxNumOfCellList):
    #level_0 is the base mesh size = min (innerBoxLength/numOfCell_X, innerBoxWidth/numOfCell_Y)
    level_0=min(innerBoxDim[0]/innerBoxNumOfCellList[0], innerBoxDim[1]/innerBoxNumOfCellList[1])
    level_1=level_0/2
    level_2=level_0/4
    level_3=level_0/8
    
    return (level_0, level_1, level_2, level_3)

def findGrowthRate(lineLen,startGridLen,numOfGrid):
    a0=startGridLen
    n=numOfGrid
    qMin=0
    qMax=1.5
    q=(qMin+qMax)/2
    for i in range(100):
        sum=a0*(1-q**n)/(1-q)
        if abs(sum-lineLen)<0.001:
            return "%.4f" % q
        elif sum > lineLen:
            qMax=q
            q=(qMin+qMax)/2
        elif sum < lineLen:
            qMin=q
            q=(qMin+qMax)/2
    return -1

app()
#case1()

#####################################################################################



#####################################################################################