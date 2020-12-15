rad -v 0 model.rif
del WP_TowerFacade.out
type WP_TowerFacade.pts | rtrace @model.opt -h -ov -I -dv- -x 1 model.oct | rcalc -e "$1 = ($1 * 47.4482686 + $2 * 119.950519 + $3 * 11.6012125) / 179.0" >> WP_TowerFacade.out
rem del WP_LowerFacade.out
rem type WP_LowerFacade.pts | rtrace @model.opt -h -ov -I -dv- -x 1 model.oct | rcalc -e "$1 = ($1 * 47.4482686 + $2 * 119.950519 + $3 * 11.6012125) / 179.0" >> WP_LowerFacade.out
