scoreboard players add #ran ccx.tmp 1
# Pessimistic default: a line that cannot even be parsed counts as failed.
scoreboard players set #ok ccx.tmp 0
function ccx:run/exec with storage ccx:run macro
execute if score #ok ccx.tmp matches 0 run scoreboard players add #fail ccx.tmp 1
