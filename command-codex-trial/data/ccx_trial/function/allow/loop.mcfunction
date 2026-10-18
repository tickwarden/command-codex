execute unless data storage ccx_trial:tmp iter[0] run return 0
data modify storage ccx_trial:tmp m set from storage ccx_trial:tmp iter[0]
data remove storage ccx_trial:tmp iter[0]
function ccx_trial:allow/test with storage ccx_trial:tmp m
execute if score #ok cxt.tmp matches 1 run return 0
function ccx_trial:allow/loop
