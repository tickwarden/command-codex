scoreboard players add #ran ccxu.tmp 1
# Pessimistic default: a line that cannot even be parsed counts as failed.
scoreboard players set #ok ccxu.tmp 0
function ccxu:run/exec with storage ccxu:run macro
execute if score #ok ccxu.tmp matches 0 run scoreboard players add #fail ccxu.tmp 1
