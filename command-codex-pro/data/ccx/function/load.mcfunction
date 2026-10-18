# Command Codex Pro - runs on every reload. Everything here is idempotent.
scoreboard objectives add ccx.run trigger
scoreboard objectives add ccx.book trigger
scoreboard objectives add ccx.opt trigger
scoreboard objectives add ccx.left dummy
scoreboard objectives add ccx.cond dummy
scoreboard objectives add ccx.clear dummy
scoreboard objectives add ccx.quiet dummy
scoreboard objectives add ccx.runs dummy
scoreboard objectives add ccx.tmp dummy
scoreboard objectives add ccx.cfg dummy
scoreboard players set #2 ccx.cfg 2
scoreboard players set #version ccx.cfg 100
# Upper bound for repeated executions per run. Change with:
#   /scoreboard players set #max_repeat ccx.cfg <ticks>
execute unless score #max_repeat ccx.cfg matches 1.. run scoreboard players set #max_repeat ccx.cfg 200