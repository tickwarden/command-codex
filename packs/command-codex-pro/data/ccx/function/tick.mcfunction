# Only players who passed the gate ever get their triggers enabled.
execute as @a[tag=ccx.allow] run function ccx:gate/enable
execute as @a[scores={ccx.book=1..}] run function ccx:book/request
execute as @a[scores={ccx.opt=1..}] run function ccx:opt/handle
execute as @a[scores={ccx.run=1..}] at @s run function ccx:run/request
execute as @a[scores={ccx.left=1..}] at @s run function ccx:run/step
