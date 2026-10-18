scoreboard players set @s cxt.book 0
execute if score #done cxt.done matches 1 run return 0
execute store result score #has cxt.tmp run clear @s minecraft:writable_book[minecraft:custom_data~{ccx_trial:1b}] 0
execute if score #has cxt.tmp matches 1.. run return run title @s actionbar {text:"Command Codex trial: you already carry one.",color:"yellow"}
function ccx_trial:book/give
