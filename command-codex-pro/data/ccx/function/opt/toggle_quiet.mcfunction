scoreboard players add @s ccx.quiet 1
scoreboard players operation @s ccx.quiet %= #2 ccx.cfg
execute if score @s ccx.quiet matches 1 run title @s actionbar {text:"Command Codex: quiet mode ON",color:"green"}
execute unless score @s ccx.quiet matches 1 run title @s actionbar {text:"Command Codex: quiet mode OFF",color:"yellow"}
