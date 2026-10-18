# Only players who passed the gate ever get their triggers enabled.
execute as @a[tag=ccxu.allow] run function ccxu:gate/enable
execute as @a[scores={ccxu.book=1..}] run function ccxu:book/request
execute as @a[scores={ccxu.opt=1..}] run function ccxu:opt/handle
execute as @a[scores={ccxu.run=1..}] at @s run function ccxu:run/request
execute as @a[scores={ccxu.left=1..}] at @s run function ccxu:run/step
