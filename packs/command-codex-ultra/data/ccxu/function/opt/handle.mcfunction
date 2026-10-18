scoreboard players operation #v ccxu.tmp = @s ccxu.opt
scoreboard players set @s ccxu.opt 0
execute unless entity @s[tag=ccxu.allow] run return run function ccxu:gate/denied
execute if score #v ccxu.tmp matches 1 run function ccxu:opt/toggle_cond
execute if score #v ccxu.tmp matches 2 run function ccxu:opt/toggle_clear
execute if score #v ccxu.tmp matches 3 run function ccxu:opt/toggle_quiet
execute if score #v ccxu.tmp matches 4 run function ccxu:run/stop
execute if score #v ccxu.tmp matches 5 run function ccxu:dry/start
execute unless score #v ccxu.tmp matches 1..5 run function ccxu:opt/help
