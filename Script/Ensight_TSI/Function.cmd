VERSION 8.26

variables: activate VelocityMagnitude
variables: evaluate El_V = ElemToNode(6,VelocityMagnitude)
variables: evaluate CaseMap_V_AM = CaseMap(4,6,El_V,1)
function: palette CaseMap_V_AM
variables: evaluate CaseMap_V_PM = CaseMap(5,6,El_V,1)
variables: activate Irradiance
part: select_byname_begin
"(CASE:Case 4)Irradiance" "(CASE:Case 5)Irradiance"
part: select_byname_end
variables: evaluate Rad = Irradiance/21
part: select_byname_begin
"(CASE:Case 4)Irradiance"
part: select_byname_end
variables: evaluate TSI_AM = 1.2+0.115*28.08+0.0019*Rad-0.3185*CaseMap_V_AM
function: palette CaseMap_V_PM
function: palette El_V
function: palette Time
function: palette TSI_AM
part: select_byname_begin
"(CASE:Case 5)Irradiance"
part: select_byname_end
variables: evaluate TSI_PM = 1.2+0.115*30.46+0.0019*Rad-0.3185*CaseMap_V_PM
