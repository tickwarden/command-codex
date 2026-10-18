# Lists authorized players that are currently online.
execute store result score #c ccxu.tmp if entity @a[tag=ccxu.allow]
tellraw @s [{text:"[Command Codex Ultra] authorized online: ",color:"light_purple"},{score:{name:"#c",objective:"ccxu.tmp"},color:"white"},{text:" ",color:"gray"},{selector:"@a[tag=ccxu.allow]"}]
