# Pops the next page and runs it. Recursive, ends when the page list is empty.
execute unless data storage ccxu:run pages[0] run return 0
scoreboard players add #idx ccxu.tmp 1
execute if score #idx ccxu.tmp > #max_lines ccxu.cfg run return 0
data remove storage ccxu:run macro.line
data remove storage ccxu:run head
data modify storage ccxu:run macro.line set from storage ccxu:run pages[0].raw
data remove storage ccxu:run pages[0]
# First character decides: empty page = no head, # = comment.
data modify storage ccxu:run head set string storage ccxu:run macro.line 0 1
execute if data storage ccxu:run head unless data storage ccxu:run {head:"#"} run function ccxu:run/attempt
# Stop-on-fail mode: the first failing command ends the pass.
execute if score @s ccxu.cond matches 1 if score #ok ccxu.tmp matches 0 run return 0
function ccxu:run/next
