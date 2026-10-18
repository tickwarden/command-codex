# Context: as the player who used /trigger cxt.run, at the player.
scoreboard players set @s cxt.run 0
execute if score #done cxt.done matches 1 run return 0
execute unless items entity @s weapon.mainhand minecraft:writable_book[minecraft:custom_data~{ccx_trial:1b}] run return run title @s actionbar {text:"Command Codex trial: hold your Codex in the main hand.",color:"yellow"}
scoreboard players set @s cxt.cd 100
data remove storage ccx_trial:run pages
data modify storage ccx_trial:run pages set from entity @s SelectedItem.components."minecraft:writable_book_content".pages
scoreboard players set #idx cxt.tmp 0
scoreboard players set #ran cxt.tmp 0
scoreboard players set #deny cxt.tmp 0
function ccx_trial:run/next
function ccx_trial:run/report
