# Trial is over: mark it, announce it, wipe every trace, then disable the pack.
scoreboard players set #done cxt.done 1
title @a times 10 80 20
title @a title {text:"Command Codex",color:"light_purple"}
title @a subtitle {text:"Trial ended - shutting down",color:"gray"}
tellraw @a [{text:"[Command Codex] ",color:"light_purple"},{text:"The trial has ended and cleaned up after itself.",color:"gray"},{text:" [Get the full version]",color:"aqua",underlined:1b,click_event:{action:"open_url",url:"https://github.com/runtoolkit/command-codex"},hover_event:{action:"show_text",value:"Open the project page"}}]
execute as @a at @s run playsound minecraft:block.note_block.bass master @s ~ ~ ~ 1 0.5
clear @a minecraft:writable_book[minecraft:custom_data~{ccx_trial:1b}]
scoreboard objectives remove cxt.run
scoreboard objectives remove cxt.book
scoreboard objectives remove cxt.cd
scoreboard objectives remove cxt.tmp
scoreboard objectives remove cxt.state
data remove storage ccx_trial:run pages
data remove storage ccx_trial:run macro
data remove storage ccx_trial:run head
data remove storage ccx_trial:cfg allow
data remove storage ccx_trial:tmp head
data remove storage ccx_trial:tmp iter
data remove storage ccx_trial:tmp m
data remove storage ccx_trial:seal v
function ccx_trial:trial/disable
