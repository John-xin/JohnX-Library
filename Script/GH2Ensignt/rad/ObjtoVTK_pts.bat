perl objchecker.pl WP_TowerFacade.obj
perl makeRadplane.pl < WP_TowerFacade.obj
if EXIST WP_TowerFacade.pts Del WP_TowerFacade.pts
Rename RadPlane.dat WP_TowerFacade.pts
if EXIST WP_TowerFacade.vtk Del WP_TowerFacade.vtk
Rename VTKPlane.vtk WP_TowerFacade.vtk
perl objchecker.pl WP_LowerFacade.obj
perl makeRadplane.pl < WP_LowerFacade.obj
if EXIST WP_LowerFacade.pts Del WP_LowerFacade.pts
Rename RadPlane.dat WP_LowerFacade.pts
if EXIST WP_LowerFacade.vtk Del WP_LowerFacade.vtk
Rename VTKPlane.vtk WP_LowerFacade.vtk
