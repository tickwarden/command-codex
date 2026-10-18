# Sets #ok to 1 when the current line starts with an allowed verb.
scoreboard players set #ok cxt.tmp 0
data modify storage ccx_trial:tmp iter set from storage ccx_trial:cfg allow
function ccx_trial:allow/loop
