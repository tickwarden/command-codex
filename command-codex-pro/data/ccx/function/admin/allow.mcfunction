# /function ccx:admin/allow {player:"Name"}  (operators only: /function needs permission level 2)
$tag $(player) add ccx.allow
$scoreboard players enable $(player) ccx.book
$scoreboard players enable $(player) ccx.opt
$scoreboard players enable $(player) ccx.run
