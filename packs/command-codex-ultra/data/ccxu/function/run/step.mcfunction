# One execution pass. Context: as the runner, at the runner.
execute unless items entity @s weapon.mainhand minecraft:writable_book[minecraft:custom_data~{ccxu:1b}] run return run function ccxu:run/lost
data remove storage ccxu:run pages
data modify storage ccxu:run pages set from entity @s SelectedItem.components."minecraft:writable_book_content".pages
scoreboard players set #ran ccxu.tmp 0
scoreboard players set #fail ccxu.tmp 0
scoreboard players set #ok ccxu.tmp 1
scoreboard players set #idx ccxu.tmp 0
function ccxu:run/next
scoreboard players remove @s ccxu.left 1
execute if score @s ccxu.left matches ..0 run function ccxu:run/finish
