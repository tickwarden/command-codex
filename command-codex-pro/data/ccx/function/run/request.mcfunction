# Context: as the player who used /trigger ccx.run, at the player.
scoreboard players operation #n ccx.tmp = @s ccx.run
scoreboard players set @s ccx.run 0
execute unless entity @s[tag=ccx.allow] run return run function ccx:gate/denied
execute unless items entity @s weapon.mainhand minecraft:writable_book[minecraft:custom_data~{ccx:1b}] run return run function ccx:run/no_book
execute if score @s ccx.left matches 1.. run return run function ccx:run/busy
execute if score #n ccx.tmp matches ..0 run scoreboard players set #n ccx.tmp 1
execute if score #n ccx.tmp > #max_repeat ccx.cfg run scoreboard players operation #n ccx.tmp = #max_repeat ccx.cfg
# The first pass happens in the same tick via ccx:tick (ccx.left >= 1).
scoreboard players operation @s ccx.left = #n ccx.tmp
scoreboard players add @s ccx.runs 1
