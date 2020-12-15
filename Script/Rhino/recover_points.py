import rhinoscriptsyntax as rs
import Rhino.Input as rip
import Rhino.Input.Custom as ric
#open point file and read
ptslist=[]
pt=[]
path=rs.WorkingFolder()
filename=rip.RhinoGet.GetFileName(ric.GetFileNameMode.OpenTextFile, "*", "select file",None)

with open(filename,"r") as f:
    for _ in range(11): #skip first 11 lines
        next(f)
    for line in f:
        data=(line.split(" "))
        if len(data)==5:
            pt=[float(data[2]),float(data[3]),float(data[4])]
            ptslist.append(pt)
    f.close()
print(len(ptslist))

#draw point
count=1
for pt in ptslist:
    pnt=rs.CreatePoint(pt[0],pt[1],pt[2])
    ptID=rs.AddPoint(pnt) 
    rs.AddText(str(count),pnt,height=1)
    count+=1

