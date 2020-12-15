import rhinoscriptsyntax as rs

#modify parameter-----------------------------
objPt=rs.ObjectsByLayer("baseCoordinate")
basePt=rs.coerce3dpoint(objPt[0])
scaleVel=rs.ObjectsByLayer("Scale_Vel")
realVel=10
scaleZ=rs.ObjectsByLayer("Scale_Z")
realZ=500
scaleVelLen=rs.CurveLength(scaleVel)
scaleZLen=rs.CurveLength(scaleZ)
#modify parameter-----------------------------

def readLine(layer):
    obj=rs.ObjectsByLayer(layer)
    ptList=rs.CurvePoints(obj)
    return ptList
    
def scaleConvert(ptList):
    cvtPtList=[]
    cvtPt=[0,0,0]
    for pt in ptList:
        cvtPt[0]=pt.X-basePt.X
        cvtPt[1]=pt.Y-basePt.Y
        cvtPt[0]=realVel*cvtPt[0]/scaleVelLen
        cvtPt[1]=realZ*cvtPt[1]/scaleZLen
        tmp=[cvtPt[0],cvtPt[1]]
        cvtPtList.append(tmp)
        
    cvtPtList.sort(key=lambda tup: tup[1]) #sort by Z
    cvtPtList[0][1]=10
    cvtPtList[-1][1]=500
    return cvtPtList
    
def write2File(f, cvtPtList,layerName):
    f.write("%s\n" %layerName)
    f.write("Z\tVel\n")
    for pt in cvtPtList:
        f.write("%.3f\t%.3f\n" %(pt[1],pt[0]))
    f.write("\n\n")
    return
    
    
f= open("readData_WindProfile.txt","w+")
layerNameList=["Line0","Line1","Line2","Line3"]
for layer in layerNameList:
    ptList=readLine(layer)
    cvtPtList=scaleConvert(ptList)
    write2File(f,cvtPtList,layer)
f.close()


