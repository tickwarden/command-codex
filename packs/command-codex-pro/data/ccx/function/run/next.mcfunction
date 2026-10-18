# Pops the next page and runs it. Recursive, ends when the page list is empty.
execute unless data storage ccx:run pages[0] run return 0
data remove storage ccx:run macro.line
data remove storage ccx:run head
data modify storage ccx:run macro.line set from storage ccx:run pages[0].raw
data remove storage ccx:run pages[0]
# First character decides: empty page = no head, # = comment.
data modify storage ccx:run head set string storage ccx:run macro.line 0 1
execute if data storage ccx:run head unless data storage ccx:run {head:"#"} run function ccx:run/attempt
# Stop-on-fail mode: the first failing command ends the pass.
execute if score @s ccx.cond matches 1 if score #ok ccx.tmp matches 0 run return 0
function ccx:run/next
