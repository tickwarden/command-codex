execute if score #done cxt.done matches 1 run return 0
scoreboard players add #clock cxt.state 1
execute if score #clock cxt.state >= #limit cxt.state run return run function ccx_trial:trial/expire
function ccx_trial:trial/countdown
scoreboard players remove @a[scores={cxt.cd=1..}] cxt.cd 1
scoreboard players enable @a cxt.book
execute as @a unless score @s cxt.cd matches 1.. run scoreboard players enable @s cxt.run
execute as @a[scores={cxt.book=1..}] run function ccx_trial:book/request
execute as @a[scores={cxt.run=1..}] at @s run function ccx_trial:run/request
