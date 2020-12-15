// Gmsh project created on Tue Jul 17 00:00:10 2018
SetFactory("OpenCASCADE");
//+
Box(1) = {-0.3, -0.6, 0, 1, 1, 1};
//+
Box(2) = {0.2, -0.6, 0, 0.5, 0.5, 0.5};
//+
Box(3) = {-0.3, -0.1, 0, 0.5, 0.5, 0.5};
//+
BooleanDifference{ Volume{1}; Delete; }{ Volume{3}; Delete; }
//+
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }
