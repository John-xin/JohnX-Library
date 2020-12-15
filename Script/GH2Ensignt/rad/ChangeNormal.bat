perl changenormals.pl < WP_TowerFacade.pts > WP_TowerFacade.tmp
del WP_TowerFacade.pts
rename WP_TowerFacade.tmp WP_TowerFacade.pts
del WP_TowerFacade.tmp
perl changenormals.pl < WP_LowerFacade.pts > WP_LowerFacade.tmp
del WP_LowerFacade.pts
rename WP_LowerFacade.tmp WP_LowerFacade.pts
del WP_LowerFacade.tmp
