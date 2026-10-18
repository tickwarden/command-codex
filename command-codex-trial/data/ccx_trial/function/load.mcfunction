# Command Codex Trial - runs on every reload.
scoreboard objectives add cxt.done dummy
# A finished trial stays finished: only retry the shutdown, create nothing.
execute if score #done cxt.done matches 1 run return run function ccx_trial:trial/disable
scoreboard objectives add cxt.run trigger
scoreboard objectives add cxt.book trigger
scoreboard objectives add cxt.cd dummy
scoreboard objectives add cxt.tmp dummy
scoreboard objectives add cxt.state dummy
# Trial length in ticks (20 ticks = 1 second). Edit this single number.
scoreboard players set #limit cxt.state 144000
scoreboard players set #1200 cxt.state 1200
# Verbs the trial may run (prefix + prefix length). No gate exists, so this list is the safety net.
data modify storage ccx_trial:cfg allow set value [{pre:"say ",n:4},{pre:"playsound ",n:10},{pre:"particle ",n:9}]
# Tamper check: the seal exists but the clock was wiped -> end the trial instead of restarting it.
execute if data storage ccx_trial:seal {v:1b} unless score #clock cxt.state matches 0.. run return run function ccx_trial:trial/expire
execute unless data storage ccx_trial:seal {v:1b} run function ccx_trial:trial/first_run
