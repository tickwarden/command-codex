scoreboard players add @s ccx.clear 1
scoreboard players operation @s ccx.clear %= #2 ccx.cfg
execute if score @s ccx.clear matches 1 run title @s actionbar {text:"Command Codex: clear-after-run ON",color:"green"}
execute unless score @s ccx.clear matches 1 run title @s actionbar {text:"Command Codex: clear-after-run OFF",color:"yellow"}
