# Appends one entry per accepted run; the log keeps the newest 50.
execute store result score #t ccxu.tmp run time query gametime
data modify storage ccxu:audit entry.uuid set from entity @s UUID
execute store result storage ccxu:audit entry.tick int 1 run scoreboard players get #t ccxu.tmp
execute store result storage ccxu:audit entry.repeat int 1 run scoreboard players get @s ccxu.left
data modify storage ccxu:audit log append from storage ccxu:audit entry
execute if data storage ccxu:audit log[50] run data remove storage ccxu:audit log[0]
