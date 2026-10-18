data modify storage ccx_trial:seal v set value 1b
scoreboard players set #clock cxt.state 0
scoreboard players operation #min cxt.tmp = #limit cxt.state
scoreboard players operation #min cxt.tmp /= #1200 cxt.state
tellraw @a [{text:"[Command Codex] ",color:"light_purple"},{text:"Trial active for ",color:"gray"},{score:{name:"#min",objective:"cxt.tmp"},color:"white"},{text:" minutes. Get your book: ",color:"gray"},{text:"/trigger cxt.book",color:"aqua",click_event:{action:"suggest_command",command:"/trigger cxt.book"}}]
