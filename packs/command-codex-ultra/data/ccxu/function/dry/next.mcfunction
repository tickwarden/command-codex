execute unless data storage ccxu:run pages[0] run return 0
scoreboard players add #pages ccxu.tmp 1
data remove storage ccxu:run macro.line
data remove storage ccxu:run head
data modify storage ccxu:run macro.line set from storage ccxu:run pages[0].raw
data remove storage ccxu:run pages[0]
data modify storage ccxu:run head set string storage ccxu:run macro.line 0 1
execute if data storage ccxu:run head unless data storage ccxu:run {head:"#"} run scoreboard players add #code ccxu.tmp 1
execute if data storage ccxu:run {head:"#"} run scoreboard players add #skip ccxu.tmp 1
execute unless data storage ccxu:run head run scoreboard players add #skip ccxu.tmp 1
function ccxu:dry/next
