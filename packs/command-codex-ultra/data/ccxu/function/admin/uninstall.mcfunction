# Removes every trace of the pack from the world, then disables it.
tag @a remove ccxu.allow
scoreboard objectives remove ccxu.run
scoreboard objectives remove ccxu.book
scoreboard objectives remove ccxu.opt
scoreboard objectives remove ccxu.left
scoreboard objectives remove ccxu.cond
scoreboard objectives remove ccxu.clear
scoreboard objectives remove ccxu.quiet
scoreboard objectives remove ccxu.runs
scoreboard objectives remove ccxu.tmp
scoreboard objectives remove ccxu.cfg
data remove storage ccxu:run pages
data remove storage ccxu:run macro
data remove storage ccxu:run head
data remove storage ccxu:audit log
data remove storage ccxu:audit entry
datapack disable "file/command-codex-ultra.zip"
datapack disable "file/command-codex-ultra"
