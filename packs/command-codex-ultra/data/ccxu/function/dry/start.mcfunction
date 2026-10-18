# Dry run: counts pages without executing anything. Context: as the player.
execute unless items entity @s weapon.mainhand minecraft:writable_book[minecraft:custom_data~{ccxu:1b}] run return run function ccxu:run/no_book
data remove storage ccxu:run pages
data modify storage ccxu:run pages set from entity @s SelectedItem.components."minecraft:writable_book_content".pages
scoreboard players set #pages ccxu.tmp 0
scoreboard players set #code ccxu.tmp 0
scoreboard players set #skip ccxu.tmp 0
function ccxu:dry/next
title @s actionbar [{text:"Dry run: ",color:"aqua"},{score:{name:"#pages",objective:"ccxu.tmp"},color:"white"},{text:" pages, ",color:"gray"},{score:{name:"#code",objective:"ccxu.tmp"},color:"green"},{text:" commands, ",color:"gray"},{score:{name:"#skip",objective:"ccxu.tmp"},color:"yellow"},{text:" skipped",color:"gray"}]
