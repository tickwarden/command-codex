scoreboard players set @s ccxu.book 0
execute unless entity @s[tag=ccxu.allow] run return run function ccxu:gate/denied
execute store result score #has ccxu.tmp run clear @s minecraft:writable_book[minecraft:custom_data~{ccxu:1b}] 0
execute if score #has ccxu.tmp matches 1.. run return run title @s actionbar {text:"Command Codex Ultra: you already carry one.",color:"yellow"}
function ccxu:book/give
