scoreboard players add @s ccxu.quiet 1
scoreboard players operation @s ccxu.quiet %= #2 ccxu.cfg
execute if score @s ccxu.quiet matches 1 run title @s actionbar {text:"Command Codex Ultra: quiet mode ON",color:"green"}
execute unless score @s ccxu.quiet matches 1 run title @s actionbar {text:"Command Codex Ultra: quiet mode OFF",color:"yellow"}
