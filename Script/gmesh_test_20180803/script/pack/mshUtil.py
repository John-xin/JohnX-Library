import rhinoscriptsyntax as rs
import os
import sqlite3 
from pack.Point import *

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