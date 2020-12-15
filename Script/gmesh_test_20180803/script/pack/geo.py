import rhinoscriptsyntax as rs
import os
import sqlite3
from pack.geoUtil import * 

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
                        tmpX=float(pt[0])
                        tmpY=float(pt[1])
                        tmpZ=float(pt[2])
                        tmpX="%.6f" % tmpX
                        tmpY="%.6f" % tmpY
                        tmpZ="%.6f" % tmpZ
                        ptDict.append({'ptIndex':countPt,'ptDictNo':countPt,'ptX':tmpX,'ptY':tmpY,'ptZ':tmpZ,'isRepeated':False,'lineLoopMark':countLine,'surfaceMark':countSurface,'volumeMark':countVolume,'layerName':layer})
                    #end for
                #end for
                rs.DeleteObjects(lines) #delete the duplicate lines
            #end for
            rs.DeleteObjects(surfaces)
        #end for
    #end for

    
    ptDict=dealWithSamePt(ptDict)
    savePtDict2DB(ptDict)
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
    c.execute('CREATE TABLE IF NOT EXISTS ptTable(ptDictNo INTEGER, ptIndex INTEGER, ptX REAL, ptY REAL, ptZ REAL, isRepeated TEXT, lineLoopMark INTEGER, surfaceMark INTEGER, volumeMark INTEGER, layerName TEXT)')
    c.execute('DELETE FROM ptTable')
    for i in range(len(ptDict)):
	entry=(ptDict[i]['ptDictNo'], ptDict[i]['ptIndex'], ptDict[i]['ptX'], ptDict[i]['ptY'], ptDict[i]['ptZ'],
	           ptDict[i]['isRepeated'], ptDict[i]['lineLoopMark'], ptDict[i]['surfaceMark'], ptDict[i]['volumeMark'], ptDict[i]['layerName'])
	c.execute('INSERT INTO ptTable VALUES (?,?,?,?,?,?,?,?,?,?)', entry)
    conn.commit()
    c.close()
    conn.close()
    
    return
	
    
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
        x=surfMarkNum
        c.execute('DELETE FROM ptTable WHERE surfaceMark=?', x)
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