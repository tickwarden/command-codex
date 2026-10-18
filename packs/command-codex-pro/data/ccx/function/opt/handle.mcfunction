scoreboard players operation #v ccx.tmp = @s ccx.opt
scoreboard players set @s ccx.opt 0
execute unless entity @s[tag=ccx.allow] run return run function ccx:gate/denied
execute if score #v ccx.tmp matches 1 run function ccx:opt/toggle_cond
execute if score #v ccx.tmp matches 2 run function ccx:opt/toggle_clear
execute if score #v ccx.tmp matches 3 run function ccx:opt/toggle_quiet
execute if score #v ccx.tmp matches 4 run function ccx:run/stop
execute unless score #v ccx.tmp matches 1..4 run function ccx:opt/help
