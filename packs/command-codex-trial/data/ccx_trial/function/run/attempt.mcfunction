function ccx_trial:allow/check
execute if score #ok cxt.tmp matches 0 run return run scoreboard players add #deny cxt.tmp 1
scoreboard players add #ran cxt.tmp 1
function ccx_trial:run/exec with storage ccx_trial:run macro
