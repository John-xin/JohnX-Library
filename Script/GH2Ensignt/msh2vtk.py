"""Provides a scripting component.
    Inputs:
        mesh: The mesh script variable
        data: The data script variable
    vtk:
        a: The a output variable"""

__author__ = "Administrator"
__version__ = "2020.02.19"

import rhinoscriptsyntax as rs
import os

NumOfVertices=len(mesh.Vertices)
NumOfFaces= len(mesh.Faces)

def output_length():
    print "Number of data is " + str(len(data))
    print "Number of meshVertices is " + str(NumOfVertices)
    print "Number of meshFaces is "+ str(NumOfFaces)

def write_vtk():
    #write mesh.Vertices
    #write mesh.Faces
    #write vertices data
    cwd = os.getcwd()
    print cwd
    f = open(cwd+"/result_output.vtk", "w")
    f.write("# vtk DataFile Version 2.0\n")
    f.write("My Test Plane\n")
    f.write("ASCII\n")
    f.write("DATASET POLYDATA\n")
    
    f.write("POINTS "+ str(NumOfVertices) +" float\n")
    #write_vertices(f)
    
    f.write("POLYGONS " + str(NumOfFaces) + " 43590\n")
    write_faces(f)
    
    f.write("POINT_DATA " + str(NumOfVertices) + "\n")
    f.write("SCALARS Variable float")
    f.write("LOOKUP_TABLE Default")
    #write_newData(f)
    
    f.close()

def write_vertices(file):
    for i in mesh.Vertices:
        file.write(str(i.X) + " " + str(i.Y) + " " + str(i.Z)+"\n")

def write_faces(file):
    for i in mesh.Faces:
        if(i.IsQuad):
            file.write("4"+ " "+ str(i.A) + " "+ str(i.B)+ " "+ str(i.C) + " "+ str(i.D) +"\n")
        else:
            file.write("3"+ " "+ str(i.A) + " "+ str(i.B)+ " "+ str(i.C) +"\n")

def write_newData(file):
        for i in mesh.Faces:
            file.write("3"+ " "+ str(i.A) + " "+ str(i.B)+ " "+ str(i.C) +"\n")

def getConnectedFaces():
    #given a vertex, get connected faces
    #calc average
    a=1

output_length()
write_vtk()




