import rhinoscriptsyntax as rs
import os
from pack.geo import  *
from pack.mshUtil import  *


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
    