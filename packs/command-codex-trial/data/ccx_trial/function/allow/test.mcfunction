# Macro function. head stays empty when the line is shorter than the prefix.
data modify storage ccx_trial:tmp head set value ""
$data modify storage ccx_trial:tmp head set string storage ccx_trial:run macro.line 0 $(n)
$execute if data storage ccx_trial:tmp {head:"$(pre)"} run scoreboard players set #ok cxt.tmp 1
