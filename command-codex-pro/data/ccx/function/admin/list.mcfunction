# Lists authorized players that are currently online.
execute store result score #c ccx.tmp if entity @a[tag=ccx.allow]
tellraw @s [{text:"[Command Codex] authorized online: ",color:"light_purple"},{score:{name:"#c",objective:"ccx.tmp"},color:"white"},{text:" ",color:"gray"},{selector:"@a[tag=ccx.allow]"}]
