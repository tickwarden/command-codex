scoreboard players set @s ccx.book 0
execute unless entity @s[tag=ccx.allow] run return run function ccx:gate/denied
execute store result score #has ccx.tmp run clear @s minecraft:writable_book[minecraft:custom_data~{ccx:1b}] 0
execute if score #has ccx.tmp matches 1.. run return run title @s actionbar {text:"Command Codex: you already carry one.",color:"yellow"}
function ccx:book/give
