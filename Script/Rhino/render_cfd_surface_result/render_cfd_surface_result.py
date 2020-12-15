import rhinoscriptsyntax as rs
import Rhino.Input as rip
import Rhino.Input.Custom as ric
#open data file and read
ptList=[]
pt=[]
valList=[]
path=rs.WorkingFolder()
filename=rip.RhinoGet.GetFileName(ric.GetFileNameMode.OpenTextFile, "*", "select file",None)

with open(filename,"r") as f:
    for _ in range(1): #skip first line
        next(f)
    for line in f:
        data=(line.split(","))
        if len(data)!=0:
            pt=[float(data[1]),float(data[2]),float(data[3])]
            ptList.append(pt)
    f.close()
print(len(ptList))


#draw point
count=1
for pt in ptList:
    pnt=rs.CreatePoint(pt[0],pt[1],pt[2])
    ptID=rs.AddPoint(pnt) 
    rs.AddText(str(count),pnt,height=1)
    count+=1
