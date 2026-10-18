scoreboard players add @s ccxu.clear 1
scoreboard players operation @s ccxu.clear %= #2 ccxu.cfg
execute if score @s ccxu.clear matches 1 run title @s actionbar {text:"Command Codex Ultra: clear-after-run ON",color:"green"}
execute unless score @s ccxu.clear matches 1 run title @s actionbar {text:"Command Codex Ultra: clear-after-run OFF",color:"yellow"}
