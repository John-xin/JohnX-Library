VERSION 8.26

part: select_byname_begin
"(CASE:Case 4)Irradiance"
part: select_byname_end
part: modify_begin
part: visible ON
part: modify_end
part: modify_begin
part: colorby_palette Rad
part: modify_end
view: perspective OFF
annotation: axis_model OFF

function: palette Rad
function: range 0 500
viewport: select_begin
 0
viewport: select_end
view_transf: function global
viewport: constant_rgb 1.000000e+000 1.000000e+000 1.000000e+000
view_transf: function global
view_transf: function global
legend: select_palette_begin
Rad
legend: select_palette_end
legend: title_name Solar_AM (W/m2)
legend: format %.2f
legend: text_rgb 0.000000e+000 0.000000e+000 0.000000e+000
legend: format %.0f

view: hidden_surface ON
file: image_format jpg
file: image_format_options Quality 75
anim_recorders: render_offscreen ON
file: image_numpasses 1
file: image_stereo current
file: image_screen_tiling 1 1
file: image_file D:\Project2\HKHA_TungTau\MC\DDRP2\Analysis\Ensight\TSI\Result\Solar_AM
file: save_image
part: modify_begin
part: visible OFF
part: modify_end


part: select_byname_begin
"(CASE:Case 5)Irradiance"
part: select_byname_end
part: modify_begin
part: visible ON
part: modify_end
part: modify_begin
part: colorby_palette Rad
part: modify_end
view_transf: function global
legend: title_name Solar_PM (W/m2)
view_transf: function global
anim_recorders: render_offscreen ON
file: image_numpasses 1
file: image_stereo current
file: image_screen_tiling 1 1
file: image_file D:\Project2\HKHA_TungTau\MC\DDRP2\Analysis\Ensight\TSI\Result\Solar_PM
file: save_image

part: modify_begin
part: visible OFF
part: modify_end

part: select_byname_begin
"(CASE:Case 4)Irradiance"
part: select_byname_end
part: modify_begin
part: visible ON
part: modify_end
part: modify_begin
part: colorby_palette TSI_AM
part: modify_end
function: palette TSI_AM

function: range 3 5
view_transf: function global
legend: select_palette_begin
TSI_AM
legend: select_palette_end
legend: format %.2f
view_transf: function global
anim_recorders: render_offscreen ON
file: image_numpasses 1
file: image_stereo current
file: image_screen_tiling 1 1
file: image_file D:\Project2\HKHA_TungTau\MC\DDRP2\Analysis\Ensight\TSI\Result\TSI_AM
file: save_image

part: modify_begin
part: visible OFF
part: modify_end
part: select_byname_begin
"(CASE:Case 5)Irradiance"
part: select_byname_end
part: modify_begin
part: visible ON
part: modify_end
part: modify_begin
part: colorby_palette TSI_PM
part: modify_end
function: palette TSI_PM

function: range 3 5
view_transf: function global
legend: select_palette_begin
TSI_PM
legend: select_palette_end
legend: format %.4f
legend: format %.2f
view_transf: function global
anim_recorders: render_offscreen ON
file: image_numpasses 1
file: image_stereo current
file: image_screen_tiling 1 1
file: image_file D:\Project2\HKHA_TungTau\MC\DDRP2\Analysis\Ensight\TSI\Result\TSI_PM
file: save_image
