# /function ccxu:admin/allow_self - authorizes the operator who runs it.
tag @s add ccxu.allow
tellraw @s [{text:"[Command Codex Ultra] ",color:"light_purple"},{text:"You are authorized. Try ",color:"gray"},{text:"/trigger ccxu.opt",color:"aqua",click_event:{action:"suggest_command",command:"/trigger ccxu.opt"}}]
