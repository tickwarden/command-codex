# /function ccx:admin/allow_self - authorizes the operator who runs it.
tag @s add ccx.allow
tellraw @s [{text:"[Command Codex] ",color:"light_purple"},{text:"You are authorized. Try ",color:"gray"},{text:"/trigger ccx.opt",color:"aqua",click_event:{action:"suggest_command",command:"/trigger ccx.opt"}}]
