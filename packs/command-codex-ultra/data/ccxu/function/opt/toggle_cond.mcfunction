scoreboard players add @s ccxu.cond 1
scoreboard players operation @s ccxu.cond %= #2 ccxu.cfg
execute if score @s ccxu.cond matches 1 run title @s actionbar {text:"Command Codex Ultra: stop-on-fail ON",color:"green"}
execute unless score @s ccxu.cond matches 1 run title @s actionbar {text:"Command Codex Ultra: stop-on-fail OFF",color:"yellow"}
