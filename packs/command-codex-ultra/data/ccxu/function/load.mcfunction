# Command Codex Ultra Pro - runs on every reload. Everything here is idempotent.
scoreboard objectives add ccxu.run trigger
scoreboard objectives add ccxu.book trigger
scoreboard objectives add ccxu.opt trigger
scoreboard objectives add ccxu.left dummy
scoreboard objectives add ccxu.cond dummy
scoreboard objectives add ccxu.clear dummy
scoreboard objectives add ccxu.quiet dummy
scoreboard objectives add ccxu.runs dummy
scoreboard objectives add ccxu.tmp dummy
scoreboard objectives add ccxu.cfg dummy
scoreboard players set #2 ccxu.cfg 2
scoreboard players set #version ccxu.cfg 200
# Page cap per pass (the vanilla book limit is 100). Change with:
#   /scoreboard players set #max_lines ccxu.cfg <pages>
execute unless score #max_lines ccxu.cfg matches 1.. run scoreboard players set #max_lines ccxu.cfg 100
# Upper bound for repeated executions per run. Change with:
#   /scoreboard players set #max_repeat ccxu.cfg <ticks>
execute unless score #max_repeat ccxu.cfg matches 1.. run scoreboard players set #max_repeat ccxu.cfg 200
