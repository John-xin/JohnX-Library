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
 
    