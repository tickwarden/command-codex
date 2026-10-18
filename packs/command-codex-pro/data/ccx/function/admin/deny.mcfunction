# /function ccx:admin/deny {player:"Name"}
$tag $(player) remove ccx.allow
$scoreboard players set $(player) ccx.left 0
$scoreboard players reset $(player) ccx.run
$scoreboard players reset $(player) ccx.book
$scoreboard players reset $(player) ccx.opt
