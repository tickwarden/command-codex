# Context: as the player who used /trigger ccxu.run, at the player.
scoreboard players operation #n ccxu.tmp = @s ccxu.run
scoreboard players set @s ccxu.run 0
execute unless entity @s[tag=ccxu.allow] run return run function ccxu:gate/denied
execute unless items entity @s weapon.mainhand minecraft:writable_book[minecraft:custom_data~{ccxu:1b}] run return run function ccxu:run/no_book
execute if score @s ccxu.left matches 1.. run return run function ccxu:run/busy
execute if score #n ccxu.tmp matches ..0 run scoreboard players set #n ccxu.tmp 1
execute if score #n ccxu.tmp > #max_repeat ccxu.cfg run scoreboard players operation #n ccxu.tmp = #max_repeat ccxu.cfg
# The first pass happens in the same tick via ccxu:tick (ccxu.left >= 1).
scoreboard players operation @s ccxu.left = #n ccxu.tmp
scoreboard players add @s ccxu.runs 1
function ccxu:audit/log
