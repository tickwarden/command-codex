# One execution pass. Context: as the runner, at the runner.
execute unless items entity @s weapon.mainhand minecraft:writable_book[minecraft:custom_data~{ccx:1b}] run return run function ccx:run/lost
data remove storage ccx:run pages
data modify storage ccx:run pages set from entity @s SelectedItem.components."minecraft:writable_book_content".pages
scoreboard players set #ran ccx.tmp 0
scoreboard players set #fail ccx.tmp 0
scoreboard players set #ok ccx.tmp 1
function ccx:run/next
scoreboard players remove @s ccx.left 1
execute if score @s ccx.left matches ..0 run function ccx:run/finish
