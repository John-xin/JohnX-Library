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
    tetMeshSize=3.0
    f= open("test.geo","w+")
    f.write("tetMeshSize=%s;\n" %tetMeshSize)
    
    lineIndex=0
    surfaceIndex=0
    volumeIndex=0
    (mGeoDict)=load2GeoDict()
    
    f.write("Point(%d)={%s,tetMeshSize};\n" %(mGeoDict[0]['ptIndex'],str(mGeoDict[0]['pt'])))
    ptIndexInSameSurf=[mGeoDict[0]['ptIndex']]
    lineLoopStr=""
    surfaceLoopStr=""
    for i in range(1,len(mGeoDict)):
        #rebuild points 
        if mGeoDict[i]['isRepeated']=='false':
            f.write("Point(%d)={%s,tetMeshSize};\n" %(mGeoDict[i]['ptIndex'],str(mGeoDict[i]['pt'])))
        #end if
        
        if mGeoDict[i]['volumeMark']==mGeoDict[i-1]['volumeMark'] and mGeoDict[i]['surfaceMark']==mGeoDict[i-1]['surfaceMark'] and i!=len(mGeoDict)-1:#pt in same surface
            ptIndexInSameSurf.append(mGeoDict[i]['ptIndex'])
        elif mGeoDict[i]['volumeMark']==mGeoDict[i-1]['volumeMark'] and mGeoDict[i]['surfaceMark']!=mGeoDict[i-1]['surfaceMark']:#pt in next surface
            #rebuild lines
            #take out two elements each time to form a line
            f.write("\n" )
            for j in range(len(ptIndexInSameSurf)-1):
                lineIndex+=1
                f.write("Line(%d)={%s,%s};\n" %(lineIndex,ptIndexInSameSurf[j],ptIndexInSameSurf[j+1]))
                lineLoopStr+=str(lineIndex)+','
            #end for
            f.write("\n" )
            
            #rebuild surfaces
            #form a line loop and surface
            surfaceIndex+=1
            f.write("Line Loop(%d)={%s};\n" %(surfaceIndex,lineLoopStr[:-1]))
            f.write("Plane Surface(%d)={%d};\n" %(surfaceIndex,surfaceIndex))
            surfaceLoopStr+=str(surfaceIndex)+','
            f.write("\n" )
            f.write("\n" )
            
            #make ptIndexInSameSurf to store ptIndex for next surface
            ptIndexInSameSurf=[mGeoDict[i]['ptIndex']]
            lineLoopStr=""
        elif mGeoDict[i]['volumeMark']!=mGeoDict[i-1]['volumeMark'] and mGeoDict[i]['surfaceMark']!=mGeoDict[i-1]['surfaceMark']:#pt in next volume
            #rebuild lines
            #take out two elements each time to form a line
            f.write("\n" )
            for j in range(len(ptIndexInSameSurf)-1):
                lineIndex+=1
                f.write("Line(%d)={%s,%s};\n" %(lineIndex,ptIndexInSameSurf[j],ptIndexInSameSurf[j+1]))
                lineLoopStr+=str(lineIndex)+','
            #end for
            f.write("\n" )
            
            #rebuild surfaces
            #form a line loop and surface
            surfaceIndex+=1
            f.write("Line Loop(%d)={%s};\n" %(surfaceIndex,lineLoopStr[:-1]))
            f.write("Plane Surface(%d)={%d};\n" %(surfaceIndex,surfaceIndex))
            surfaceLoopStr+=str(surfaceIndex)+','
            f.write("\n" )
            f.write("\n" )
            
            #rebuild volumes
            volumeIndex+=1
            f.write("Surface Loop(%d)={%s};\n" %(volumeIndex,surfaceLoopStr[:-1]))
            f.write("Volume(%d)={%d};\n" %(volumeIndex,volumeIndex))
            f.write("\n" )
            f.write("\n" )
            f.write("\n" )
            
            #make ptIndexInSameSurf to store ptIndex for next surface
            ptIndexInSameSurf=[mGeoDict[i]['ptIndex']]
            lineLoopStr=""
            surfaceLoopStr=""
        elif i==len(mGeoDict)-1: #last element
            ptIndexInSameSurf.append(mGeoDict[i]['ptIndex'])
            #rebuild lines
            #take out two elements each time to form a line
            f.write("\n" )
            for j in range(len(ptIndexInSameSurf)-1):
                lineIndex+=1
                f.write("Line(%d)={%s,%s};\n" %(lineIndex,ptIndexInSameSurf[j],ptIndexInSameSurf[j+1]))
                lineLoopStr+=str(lineIndex)+','
            #end for
            f.write("\n" )
            
            #rebuild surfaces
            #form a line loop and surface
            surfaceIndex+=1
            f.write("Line Loop(%d)={%s};\n" %(surfaceIndex,lineLoopStr[:-1]))
            f.write("Plane Surface(%d)={%d};\n" %(surfaceIndex,surfaceIndex))
            surfaceLoopStr+=str(surfaceIndex)+','
            f.write("\n" )
            f.write("\n" )
            
            #rebuild volumes
            volumeIndex+=1
            f.write("Surface Loop(%d)={%s};\n" %(volumeIndex,surfaceLoopStr[:-1]))
            f.write("Volume(%d)={%d};\n" %(volumeIndex,volumeIndex))
            f.write("\n" )
            f.write("\n" )
            f.write("\n" )
    #end for
    
    #boolean
    
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


def load2GeoDict():
    objs=rs.ObjectsByLayer("Surr",False) #return polysurfaces id list
    countVolume=0
    countSurface=0
    countSurfaceLoop=0
    countLine=0
    countLineLoop=0
    countPt=0
    geoDict=[] #define empty list
    volNumInLayer=0
    surfNumInVol=[]
    ptsNumInSurf=[]
    for obj in objs: #each obj stands for a polysurface i.e a volume
        countVolume+=1
        surfaces=rs.ExplodePolysurfaces(obj)
        for surface in surfaces:
            countSurface+=1
            lines=rs.DuplicateSurfaceBorder(surface) #return a closed line
            pts=rs.CurvePoints(lines) #return edit points in the line
            for pt in pts: #ignore the last point as it is same as the first point
                countPt+=1
                geoDict.append({'ptIndex':countPt,'pt':pt,'isRepeated':'false','surfaceMark':countSurface,'volumeMark':countVolume})
            #end for
            rs.DeleteObjects(lines) #delete the duplicate lines
        #end for
        rs.DeleteObjects(surfaces)
    #end for


    #same point location is assigned with same pointId in geoDict - this is a O(n^2), which can be optimized by balance tree data structure
    for i in range(len(geoDict)):
        for j in range(len(geoDict)):
            if geoDict[i]['pt']==geoDict[j]['pt'] and i!=j and geoDict[i]['ptIndex']!=geoDict[j]['ptIndex']:
                geoDict[j]['ptIndex']=geoDict[i]['ptIndex']
                geoDict[j]['isRepeated']='true'
        #end for
    #end for
    
    
    return geoDict


rhino2gmsh()
