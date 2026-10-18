scoreboard players set @s ccx.left 0
execute unless score @s ccx.quiet matches 1 run function ccx:run/report
execute if score @s ccx.clear matches 1 run function ccx:book/wipe
