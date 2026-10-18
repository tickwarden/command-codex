scoreboard players add @s ccx.cond 1
scoreboard players operation @s ccx.cond %= #2 ccx.cfg
execute if score @s ccx.cond matches 1 run title @s actionbar {text:"Command Codex: stop-on-fail ON",color:"green"}
execute unless score @s ccx.cond matches 1 run title @s actionbar {text:"Command Codex: stop-on-fail OFF",color:"yellow"}
