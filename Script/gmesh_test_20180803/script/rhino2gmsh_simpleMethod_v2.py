import rhinoscriptsyntax as rs
import os


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
    
    
def rhino2gmsh():
    #layerList=("block1_front","block2_back","block3_right","block4_left","block5_top","dummy")
    layerList=("dummy2","test")
    meshSizeDict=[]
    meshSizeDict.append({'layerName':layerList[0],'meshSize':6,'meshSizeName':"meshSize_"+layerList[0]})
    meshSizeDict.append({'layerName':layerList[1],'meshSize':6,'meshSizeName':"meshSize_"+layerList[1]})
    #meshSizeDict.append({'layerName':layerList[2],'meshSize':6,'meshSizeName':"meshSize_"+layerList[2]})
    #meshSizeDict.append({'layerName':layerList[3],'meshSize':6,'meshSizeName':"meshSize_"+layerList[3]})
    #meshSizeDict.append({'layerName':layerList[4],'meshSize':6,'meshSizeName':"meshSize_"+layerList[4]})
    #meshSizeDict.append({'layerName':layerList[5],'meshSize':3,'meshSizeName':"meshSize_"+layerList[5]})
    
    mPtDict=load2GeoDict(layerList)
    mLineDict=buildLineDict(mPtDict)
    mLineLoopDict=buildLineLoopDict(mLineDict)
    mSurfDict=buildSurfDict(mLineLoopDict)
    mVolDict=buildVolDict(mSurfDict)
    
    f= open("single.geo","w+")
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
    
    setPhysical()
    setMeshSize()
    
    f.close()
    return
    
def addDummyBox():
    objs1=rs.ObjectsByLayer("Surr",False)
    objs2=rs.ObjectsByLayer("Proj",False)
    objs=objs1+objs2
    myBox=rs.BoundingBox(objs)
    newBoxId=offsetBox(myBox,10)
    rs.ObjectLayer(newBoxId,"dummy")
    return

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
                        ptDict.append({'ptIndex':countPt,'ptDictNo':countPt,'ptX':round(pt[0],6),'ptY':round(pt[1],6),'ptZ':round(pt[2],6),'isRepeated':False,'lineLoopMark':countLine,'surfaceMark':countSurface,'volumeMark':countVolume,'layerName':layer})
                    #end for
                #end for
                rs.DeleteObjects(lines) #delete the duplicate lines
            #end for
            rs.DeleteObjects(surfaces)
        #end for
    #end for
    ptDict=dealWithSamePt(ptDict)
    return ptDict

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
    

#addDummyBox()
def test():
    
    
    return
    

def dealWithSamePt(ptDict):
    #same point location is assigned with same pointId in ptDict - this is a O(n^2), which can be optimized by balance tree data structure
    #ptDict[1]={ptIndex:1, ptCoordinate:pt, isRepeated, surfaceMark:1, volumeMark:1}
    #if ptDict[5]={ptIndex:5, ptCoordinate:sameAs pt, isRepeated, surfaceMark:1, volumeMark:1} has ptCoordinate same as ptDict[1]
    #transfer2 ptDict[5]={ptIndex:1, ptCoordinate:sameAs pt, isRepeated, surfaceMark:1, volumeMark:1}
    for i in range(len(ptDict)):
        for j in range(len(ptDict)):
            if i!=j and ptDict[i]['ptX']==ptDict[j]['ptX'] and ptDict[i]['ptY']==ptDict[j]['ptY'] and ptDict[i]['ptZ']==ptDict[j]['ptZ'] and ptDict[i]['ptIndex']!=ptDict[j]['ptIndex']:
                ptDict[j]['ptIndex']=ptDict[i]['ptIndex']
                ptDict[j]['isRepeated']=True
        #end for
    #end for
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
            lineDict.append({'lineIndex':lineIndex,'ptIndexList':(ptDict[i-1]['ptIndex'],ptDict[i]['ptIndex']),'signedLineIndex':lineIndex,'isRepeated':False,'lineLoopMark':ptDict[i]['lineLoopMark'],'surfaceMark':ptDict[i]['surfaceMark'],'volumeMark':ptDict[i]['volumeMark']})
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
    return lineDict
    
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
    for i in range(len(surfDict)):
        for j in range(len(surfDict)):
            if isSame(surfDict[i]['lineLoopIndexList'],surfDict[j]['lineLoopIndexList']) and surfDict[i]['surfIndex']!=surfDict[j]['surfIndex'] and i!=j:
                surfDict[j]['surfIndex']=surfDict[i]['surfIndex']
                surfDict[j]['isRepeated']=True
    return surfDict
    
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
    
def setPhysical(ptDict):
    
    return

def setMeshSize():
    
    return
    
def findSurfIndexByPts(pts,ptDict)
    
    return
rhino2gmsh()