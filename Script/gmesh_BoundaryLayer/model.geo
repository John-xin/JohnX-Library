// geo file for meshing with GMSH meshing software created by FreeCAD
 
// open brep geometry
Merge "./Box_Geometry.brep";
 
// group data
//Physical Surface("FEMMeshGroup") = {6};
 
Physical Surface("FemConstraintFixed") = {1};
Physical Surface("FemConstraintForce") = {2};
 
// Characteristic Length
// Characteristic Length according CharacteristicLengthMap
// Face6
//Characteristic Length { 3, 1, 7, 5 } = 100.0;
 
// min, max Characteristic Length
Mesh.CharacteristicLengthMax = 1e+22;
Mesh.CharacteristicLengthMin = 0.0;
 
// optimize the mesh
Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 0;
Mesh.HighOrderOptimize = 0;  //probably needs more lines off adjustment in geo file
 
// mesh order
Mesh.ElementOrder = 1;
 
 
// boundary layer, need background mesh
Field[4] = BoundaryLayer;
//Field[4].EdgesList = {3, 1,};  // EdgesList for 2D, not necessary for 3D BL
Field[4].FacesList = {1};  // FacesList  for 3D,  
Field[4].hfar = 100;
Field[4].hwall_n = 10;
Field[4].hwall_t = 9;
Field[4].thickness = 100;  // must be bigger than hwall_n
Field[4].ratio = 1.1;
 
BoundaryLayer Field = 4;
 
 
// mesh algorithm
// 2D mesh algorithm (1=MeshAdapt, 2=Automatic, 5=Delaunay, 6=Frontal, 7=BAMG, 8=DelQuad)
Mesh.Algorithm = 2;  //  2 and 8 both working for 3D BL
// 3D mesh algorithm (1=Delaunay, 2=New Delaunay, 4=Frontal, 5=Frontal Delaunay, 6=Frontal Hex, 7=MMG3D, 9=R-tree)
Mesh.Algorithm3D = 8;
// meshing
Mesh  3;
 
// save
Mesh.Format = 2;
// For each group save not only the elements but the nodes too.;
Mesh.SaveGroupsOfNodes = 1;
// Needed for Group meshing too, because for one material there is no group defined;
// Ignore Physical definitions and save all elements;
Mesh.SaveAll = 1;
Save "./Box_Mesh_TmpGmsh.unv";
 
 
//////////////////////////////////////////////////////////////////////
// GMSH documentation:
// http://gmsh.info/doc/texinfo/gmsh.html#Mesh
//
// We do not check if something went wrong, like negative jacobians etc. You can run GMSH manually yourself: 
//
// to see full GMSH log, run in bash:
// /usr/bin/gmsh - /tmp/shape2mesh.geo
//
// to run GMSH and keep file in GMSH GUI (with log), run in bash:
// /usr/bin/gmsh /tmp/shape2mesh.geo