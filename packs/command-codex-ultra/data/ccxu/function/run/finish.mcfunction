scoreboard players set @s ccxu.left 0
execute unless score @s ccxu.quiet matches 1 run function ccxu:run/report
execute if score @s ccxu.clear matches 1 run function ccxu:book/wipe
