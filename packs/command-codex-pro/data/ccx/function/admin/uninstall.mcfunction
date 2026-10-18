# Removes every trace of the pack from the world, then disables it.
tag @a remove ccx.allow
scoreboard objectives remove ccx.run
scoreboard objectives remove ccx.book
scoreboard objectives remove ccx.opt
scoreboard objectives remove ccx.left
scoreboard objectives remove ccx.cond
scoreboard objectives remove ccx.clear
scoreboard objectives remove ccx.quiet
scoreboard objectives remove ccx.runs
scoreboard objectives remove ccx.tmp
scoreboard objectives remove ccx.cfg
data remove storage ccx:run pages
data remove storage ccx:run macro
data remove storage ccx:run head
datapack disable "file/command-codex-pro.zip"
datapack disable "file/command-codex-pro"
