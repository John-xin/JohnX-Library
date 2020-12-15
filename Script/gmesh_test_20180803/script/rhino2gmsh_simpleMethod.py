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
    #rebuild points 
    f.write("tetMeshSize=%s\n" %tetMeshSize)
    #rebuild lines
    f.write("Point()={%s,%s,%s,%s};\n" %(tetMeshSize,tetMeshSize,tetMeshSize,tetMeshSize))
    #rebuild surfaces
    
    #rebuild volumes
    
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

f= open("test.geo","w+")
tetMeshSize=3.0

objs=rs.ObjectsByLayer("Surr",False) #return polysurfaces id list
volumeNum=["do not use first item"]
countVolume=0
surfaceNum=["do not use first item"]
countSurface=0
countSurfaceLoop=0
lineNum=["do not use first item"]
countLine=0
countLineLoop=0
ptNum=["do not use first item"]
countPt=0
ptDict=[]
for obj in objs: #each obj stands for a polysurface i.e a volume
    surfaces=rs.ExplodePolysurfaces(obj)
    surfaceLoopNum=""
    for surface in surfaces:
        lines=rs.DuplicateSurfaceBorder(surface)
        for line in lines:
            pts=rs.CurvePoints(line)
            for iterPt in range(0,len(pts)-1): #ignore the last point as it is same as the first point
                countPt+=1
                ptNum.append(countPt)
                ptDict.append({'ptId':countPt,'pt':pts[iterPt]})
                f.write("Point(%d)={%f,%f,%f,tetMeshSize};\n" %(ptNum[countPt],pts[iterPt][0],pts[iterPt][1],pts[iterPt][2]))
                
            lineLoopNum=""
            numOfPts=len(pts)-1
            for iterLine in range(0,numOfPts):
                countLine+=1
                lineNum.append(countLine)
                startPtNum=countPt-numOfPts+iterLine+1
                if iterLine==numOfPts-1: #last iteration
                    endPtNum=countPt-numOfPts+1 #set back to startPtNum
                else:
                    endPtNum=countPt-numOfPts+iterLine+2
                f.write("Line(%d)={%d,%d};\n" %(countLine,startPtNum,endPtNum))
                lineLoopNum= str(lineLoopNum)+str(countLine)+','
                
            lineLoopNum=lineLoopNum[:-1] #ignore last character
            countLineLoop+=1
            f.write("Line Loop(%d)={%s};\n" %(countLineLoop,lineLoopNum))
            
        rs.DeleteObjects(lines)
        countSurface+=1
        f.write("Plane Surface(%d)={%d};\n" %(countSurface,countLineLoop))
        surfaceLoopNum= str(surfaceLoopNum)+str(countSurface)+','
    
    surfaceLoopNum=surfaceLoopNum[:-1]
    countSurfaceLoop+=1
    f.write("Surface Loop(%d)={%s};\n" %(countSurfaceLoop,surfaceLoopNum))
    countVolume+=1
    f.write("Volume(%d)={%d};\n" %(countVolume,countSurfaceLoop))
    rs.DeleteObjects(surfaces)
    
f.close()
