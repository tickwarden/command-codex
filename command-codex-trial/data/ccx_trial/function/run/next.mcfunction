# Pops the next page. The trial runs at most 10 pages per run.
execute unless data storage ccx_trial:run pages[0] run return 0
scoreboard players add #idx cxt.tmp 1
execute if score #idx cxt.tmp matches 11.. run return 0
data remove storage ccx_trial:run macro.line
data remove storage ccx_trial:run head
data modify storage ccx_trial:run macro.line set from storage ccx_trial:run pages[0].raw
data remove storage ccx_trial:run pages[0]
data modify storage ccx_trial:run head set string storage ccx_trial:run macro.line 0 1
execute if data storage ccx_trial:run head unless data storage ccx_trial:run {head:"#"} run function ccx_trial:run/attempt
function ccx_trial:run/next
