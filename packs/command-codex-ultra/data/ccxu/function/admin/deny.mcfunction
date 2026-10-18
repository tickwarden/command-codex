# /function ccxu:admin/deny {player:"Name"}
$tag $(player) remove ccxu.allow
$scoreboard players set $(player) ccxu.left 0
$scoreboard players reset $(player) ccxu.run
$scoreboard players reset $(player) ccxu.book
$scoreboard players reset $(player) ccxu.opt
