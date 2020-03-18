import redis
import time
import json
import uuid
import random
from copy import deepcopy
import traceback
import sys

#load game script (api helper)
try:
    import game
except:
    pass

#we'll give ourselves 50 millisecond buffer plus or minus to avoid ticking more often than we need to
graceBuffer = 50

playerData = []
playerIDList = []
mapData = {}
mapNPCs = []
mapDoors = []
mapShots = []
mapID = -1
mapItems = []
professionDB = []

pos = {}
pos["x"] = 0
pos["y"] = 0
pos["dir"] = 0
pos["map_id"] = -1
tiles = {}
tiles["layers"] = [-1 for x in range(10)]
tiles["type"] = 0
tiles["data"] = {}


mapShotTemplate = {}
mapShotTemplate["shooter_type"] = 0
mapShotTemplate["shooter_id"] = -1
mapShotTemplate["item_id"]  = -1
mapShotTemplate["pos"] = {}
mapShotTemplate["pos"]["x"] = 0
mapShotTemplate["pos"]["y"] = 0
mapShotTemplate["pos"]["dir"] = 0
mapShotTemplate["pos"]["map_id"] = 0

mapShotsTemplate = []
for i in range(50):
    mapShotsTemplate.append(mapShotTemplate)

xyTemplate = {}
xyTemplate["x"] = -1
xyTemplate["y"] = -1
mapDoorTemplate = []
for i in range(20):
    mapDoorTemplate.append(deepcopy(xyTemplate))

mapItemTemplate = {}
mapItemTemplate["item_id"] = -1
mapItemTemplate["amount"] = 0
mapItemTemplate["uses"] = 0
mapItemTemplate["x"] = 0
mapItemTemplate["y"] = 0

mapItemsTemplate = []
for i in range(200):
    mapItemsTemplate.append(deepcopy(mapItemTemplate))
#mapItemsTemplate = mapItemTemplate * 200

itemDB = None
lastItemRefresh = 0

professionDB = None
lastProfessionRefresh = 0

mobDB = None

shopDB = None

mapTemplate = {}
mapTemplate["hall_id"] = -1
mapTemplate["boot_map"] = pos
mapTemplate["map_north_id"] = -1
mapTemplate["map_east_id"] = -1
mapTemplate["map_south_id"] = -1
mapTemplate["map_west_id"] = -1
mapTemplate["forbid_attack"] = False
mapTemplate["indoors"] = False
mapTemplate["moral"] = 0
mapTemplate["forbid_ranged"] = False
mapTemplate["author"] = ''
mapTemplate["locked"] = False
mapTemplate["tiles"] = [[tiles] * 12 for i in range(12)]
mapTemplate["protect_npcs"] = False
mapTemplate["music_id"] = -1
mapTemplate["spawn_npc_ids"] = [-1 * 20]
mapTemplate["data"] = {}
mapTemplate["death_map"] = pos
mapTemplate["name"] = ''

mapNPCTemplate = {}
mapNPCTemplate["npc_id"] = -1
mapNPCTemplate["sprite"] = 0
mapNPCTemplate["scale"] = 0
mapNPCTemplate["vitals"] = {}
mapNPCTemplate["vitals"]["hp"] = 0
mapNPCTemplate["vitals"]["mp"] = 0
mapNPCTemplate["vitals"]["sp"] = 0
mapNPCTemplate["pos"] = pos

mapNPCsTemplate = []
for i in range(20):
    mapNPCsTemplate.append(deepcopy(mapNPCTemplate))

mobMetaTemplate = {}
mobMetaTemplate["data"] = {}
mobMetaTemplate["aggroList"] = {}
mobMetaTemplate["respawnTime"] = 0
mobMetaTemplate["nextTick"] = -1
mobMetaTemplate["npc_id"] = -1
#playerMetaTemplate["itemsPickedUp"] = {}
#playerMetaTemplate["itemsPickedUp"] = {}

mapMetaShotTemplate = {}
mapMetaShotTemplate["nextTick"] = 0
mapMetaShotTemplate["movesLeft"] = 0
mapMetaShotTemplate["x"] = 0
mapMetaShotTemplate["y"] = 0


mapMetaTemplate = {}
mapMetaTemplate["mobs"] = [mobMetaTemplate] * 20
mapMetaTemplate["players"] = {} #playerMetaTemplate
mapMetaTemplate["spawnItems"] = {}
mapMetaTemplate["doors"] = {}
mapMetaTemplate["shots"] = []
for i in range(50):
    mapMetaTemplate["shots"].append(deepcopy(mapMetaShotTemplate))

#mapMetaTemplate[""]

r = redis.Redis(host='localhost',port=6379,db=0)

scripts = {}
scriptPackets = {}

def prepScript(scriptName):
    global scripts
    curTime = int(time.time())
    if scripts.has_key(str(scriptName)):
        lastLoad = int(scripts[str(scriptName)])
        if (lastLoad + 10) > curTime:
            #print "not loading"
            #return, we've already loaded this 'recently'
            return
    scriptContent = r.get("script_" + str(scriptName))
    if scriptContent != None:
        scripts[str(scriptName)] = curTime + 10
        tmp = open("script_" + str(scriptName) + ".py","w+")
        tmp.write(str(scriptContent))
        tmp.close()
    else:
        scripts[str(scriptName)] = curTime

def loadScriptPackets():
    global scriptPackets
    for playerID in scriptPackets:
        for i in range(len(scriptPackets[str(playerID)])):
            sendPacketToPlayer(scriptPackets[str(playerID)][i],playerID)
    scriptPackets = {}

def professionCheck(reqProfession,professionID):
    checkNum = reqProfession >> professionID
    return (checkNum & 1)


def sendVariablesToScript():
    global playerData
    global playerIDList
    global mapData
    global mapNPCs
    global mapDoors
    global mapShots
    global mapID
    global mapItems
    global mobDB
    global itemDB
    global mapMeta
    global scriptPackets
    loadItemDB()
    loadMobDB()
    loadProfessionDB()

    scriptPackets = {}
    loadMe = {}
    loadMe["playerData"] = playerData
    loadMe["playerIDList"] = playerIDList
    loadMe["mapData"] = mapData
    loadMe["mapNPCs"] = mapNPCs
    loadMe["mapDoors"] = mapDoors
    loadMe["mapShots"] = mapShots
    loadMe["mapID"] = mapID
    loadMe["mapItems"] = mapItems
    loadMe["mobDB"] = mobDB
    loadMe["itemDB"] = itemDB
    loadMe["mapMeta"] = mapMeta
    loadMe["professionDB"] = professionDB
    game.loadVariables(loadMe)

def loadVariablesFromScript():
    global playerData
    global playerIDList
    global mapData
    global mapNPCs
    global mapDoors
    global mapShots
    global mapID
    global mapItems
    global mobDB
    global itemDB
    global mapMeta
    global scriptPackets
    loadMe = game.getVariables()
    if loadMe.has_key('playerData') and loadMe.has_key('playerIDList') and loadMe.has_key('mapData') and loadMe.has_key('mapNPCs') and loadMe.has_key('mapDoors') and loadMe.has_key('mapShots') and loadMe.has_key('mapID') and loadMe.has_key('mapItems') and loadMe.has_key('mobDB') and loadMe.has_key('itemDB') and loadMe.has_key('mapMeta'):
#        print "loading variables..."
        playerData = loadMe["playerData"]
        playerIDList = loadMe["playerIDList"]
        mapData = loadMe["mapData"]
        mapNPCs = loadMe["mapNPCs"]
        mapDoors = loadMe["mapDoors"]
        mapShots = loadMe["mapShots"]
        mapID = loadMe["mapID"]
        mapItems = loadMe["mapItems"]
        mobDB = loadMe["mobDB"]
        itemDB = loadMe["itemDB"]
        mapMeta = loadMe["mapMeta"]

        scriptPackets = loadMe["scriptPackets"]

def sendPacketToPlayer(packetToSend,playerID):
    print("Getting player session ID...")
    tmp = r.get(str(playerID) + "2SID")
    if tmp != None:
        print("socket info:" + str(tmp))
        connInfo = tmp.split(" ")
        socketServer = connInfo[0]
        socketID = connInfo[1]
        print("wsQ" + str(socketServer) + " setting:" +str(socketID) + " " + str(packetToSend))
        PL.rpush("wsQ" + str(socketServer),str(socketID) + " " + str(packetToSend))
    else:
        #leaveMap(playerID,-1)
        PL.rpush("map" + str(mapID) + "removePlayers",str(playerID))
        print("Could not send packet to playerID[" + str(playerID) + "] as they do not have a socketID or socketServer mapping..")

def sendToAllOnMap(packetToSend,excluded = None):
    if packetToSend != "":
#        print "sending..." + str(packetToSend) + " to all on map..."
        for i in range(len(playerIDList)):
#            print "excluded =" + str(excluded) + " playerIDList[" + str(i) + "]=" + str(playerIDList[i])
            if excluded == None or int(excluded) != int(playerIDList[i]):
                sendPacketToPlayer(packetToSend,playerIDList[i])

def unknown(a = None,b = None):
    print "unable to handle this type yet.."
    return

def saveAccountSettings(message,playerID):
    loadAccount = r.get("aD_" + str(playerID))
    if loadAccount != None:
        accountDetails = json.loads(loadAccount)
        accountDetails["settings"] = message["settings"]
        PL.set('aD_' + str(playerID),json.dumps(accountDetails))
        

def processPacket(processPacket):
    print ("process:" + str(processPacket))
    tmp = processPacket.split(" ")
    playerID = int(tmp[0])
    print ("tmp[1:]" + str(tmp[1:]))
    message = json.loads(" ".join(tmp[1:]))
    type = int(message["type"])
    switcher = {
        5: parseChat,
        6: playerMove,
        7: handleAttack,
        8: trainStat,
        9: useItem,
        10: pickupItem,
        11: handleTrade, 
        12: saveMapData,
        13: saveItem,
        14: saveNPC,
        15: saveShop,
        18: saveProfession,
        20: dropItem,
        22: handleClick,
        23: saveAccountSettings,
        24: handleRepair,
        26: saveScript,
        31: handleSell,
        32: hackAttempt
    }
    func = switcher.get(type,unknown)
    func(message,playerID)
    

def hackAttempt(message,playerID):
    playerIndex=playerIDToIndex(playerID)
    if playerIndex > -1: 
        if int(playerData[playerIndex]["access"]) == 0:
            sendPacketToPlayer('CLOSED',playerID) 
            packetToSend = genMessage(str(playerData[playerIndex]["name"]) + " has been disconnected for a hacking attempt!",0,'#696969')
            #leaveMap(playerID,-1) #causes issuess
            sendToEveryoneOnline(packetToSend)
        

def playerIDToIndex(playerID):
    for i in range(len(playerIDList)):
#        print("playerID(" + str(playerID) + ") == playerIDList[" + str(i) + "](" + str(playerIDList[i]) + ")?")
        if int(playerID) == int(playerIDList[i]):
#            print("Found player ID index")
            return i
    return -1

def spawnCharacter(playerIndex = None,playerID = None):
    if playerIndex == None and playerID == None:
        return
    elif playerIndex == None:
        playerIndex = int(playerIDToIndex(playerID))
    elif playerID == None:
        playerID = int(playerIDList[playerIndex])
    sendJson = {}
    sendJson["type"] = 110
    sendJson["player_id"] = int(playerID)
    sendJson["name"] = playerData[playerIndex]["name"]
    sendJson["sprite"] = playerData[playerIndex]["sprite"]
    sendJson["guild_id"] = playerData[playerIndex]["guild_id"]
    sendJson["access"] = playerData[playerIndex]["access"]
    sendJson["color"] = playerData[playerIndex]["color"]
    sendJson["killer"] = playerData[playerIndex]["killer"]
    sendJson["vitals"] = playerData[playerIndex]["vitals"]
    sendJson["max_vitals"] = playerData[playerIndex]["max_vitals"]
    sendJson["pos"] = playerData[playerIndex]["pos"]
    return json.dumps(sendJson)
    #return '{"type":110,"player_id":' + str(playerID) + ',"name":"' + str(playerData[playerIndex].name) + '","sprite":' + str(playerData[playerIndex].sprite) + ',"guild_id":' + str(playerData[playerIndex].sprite

def genWindow(window,message = ''):
    packet = {}
    packet["type"] = 100
    packet["win"] = window
    packet["message"] = message
    return json.dumps(packet)

def saveMapData(message,playerID):
    global mapData
    global mapMeta
    global mapNPCs
    playerIndex=playerIDToIndex(playerID)
    if int(playerData[playerIndex]["access"]) > 0:
        mapData = message["map"]
        sendToAllOnMap('{"type":106,"map_id":' + str(mapID) + ',"map":' + json.dumps(message["map"]) + '}')
        if mapData["music_id"] > -1:
            sendToAllOnMap('{"type":124,"music_id":' + str(mapData["music_id"]) + '}') 
        for i in range(len(playerIDList)):
            sendToAllOnMap(spawnCharacter(int(i)))
        mapNPCs = deepcopy(mapNPCsTemplate)
        mapMeta = deepcopy(mapMetaTemplate)
        sendToAllOnMap(genAllNPCUpdate())
        sendPacketToPlayer(genWindow('winGame'),playerID)

def despawnPlayer(playerID):
    packet = {}
    packet["type"] = 111
    packet["player_id"] = playerID
    packet["map_id"] = mapID
    return json.dumps(packet)

def handleAttack(message,playerID):
    if message.has_key('target_id') and message.has_key('target_type') and message.has_key('speed') and message.has_key('attacking'):
        target_id = int(message["target_id"])
        target_type = int(message["target_type"])
        speed = int(message["speed"])
        attacking = message["attacking"]
        scriptOverride = 0
        try:
            prepScript('attack')
            import script_attack
            reload(script_attack)
            if "handleAttack" in dir(script_attack):
                sendVariablesToScript()
                scriptOverride = getattr(script_attack,'handleAttack')(playerID,target_type,target_id,attacking)
                print "script override from handleAttack:" + str(scriptOverride)
                loadVariablesFromScript()
            loadScriptPackets()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            print 'attack script failed'
            pass

def trainStat(message,playerID):
    playerIndex=playerIDToIndex(playerID)
    if message.has_key("stat_id") and playerIndex > -1:
        stat_id = int(message["stat_id"])
        if int(playerData[playerIndex]["train_points"]) > 0 and stat_id >= 0 and stat_id < 4:
            playerData[playerIndex]["train_points"] -= 1
            stat = [ 'str','def','mag','spd' ][stat_id]
            playerData[playerIndex]["stats"][str(stat)] += 1

            calculateMaxVitals(playerID)            
            sendPacketToPlayer(reloadCharacterPacket(playerIndex),playerID)

def calculateMaxVitals(playerID):
    playerIndex=playerIDToIndex(playerID)
    if playerIndex > -1:
        loadProfessionDB()
        profID = playerData[playerIndex]["profession_id"]
        playerStr = playerData[playerIndex]["stats"]["str"]
        playerDef = playerData[playerIndex]["stats"]["def"]
        playerMag = playerData[playerIndex]["stats"]["mag"]
        playerSpd = playerData[playerIndex]["stats"]["spd"]
        baseHP = professionDB[profID]["vitals"]["hp"]
        baseMP = professionDB[profID]["vitals"]["mp"]
        baseSP = professionDB[profID]["vitals"]["sp"]
        playerData[playerIndex]["max_vitals"]["hp"] = baseHP + (playerStr * 1.5) + (playerDef * 3) + playerMag + (playerSpd * 2)
        playerData[playerIndex]["max_vitals"]["mp"] = baseMP + playerMag
        playerData[playerIndex]["max_vitals"]["sp"] = baseSP + (playerSpd * 2)


def handleClick(message,playerID):
    if message.has_key('x') and message.has_key('y'):
        clickX = int(message["x"])
        clickY = int(message["y"])
        scriptOverride = 0
#        if 1 == 1:
        try:
            prepScript('click')
            import script_click
            reload(script_click)
            if "handleClick" in dir(script_click):
                sendVariablesToScript()
                scriptOverride = getattr(script_click,'handleClick')(playerID,clickX,clickY)
                print "script override from handleClick:" + str(scriptOverride)
                loadVariablesFromScript()
            loadScriptPackets()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            print 'click script failed'
#    if scriptOverride == 0:
#        if canSwingFront(

def canSwingFront(x,y,d):
    #first we find whats infront of us
    if d == 0:
        y += 1
    elif d == 1:
        x -= 1
    elif d == 2:
        x += 1
    elif d == 3:
        y -= 1
    #nothing can exist outside of the map; so no point looking
    if y < 0 or y > 11 or x < 0 or x > 11:
        return (-1,-1)
    elif mapData["forbid_attack"] == True:
        return (-1,-1)
    if mapData["protect_npcs"] == False:
        for i in range(len(mapNPCs)):
            if int(mapNPCs[i]["npc_id"]) > -1 and int(mapNPCs[i]["vitals"]["hp"]) > 0:
                if mapNPCs[i]["pos"]["x"] == x and mapNPCs[i]["pos"]["y"] == y:
                    return (2,i)
    if mapData["moral"] == 1:
        for i in range(len(playerIDList)):
            if playerData[i]["vitals"]["hp"] > 0:
                if playerData[i]["pos"]["x"] == x and playerData[i]["pos"]["y"] == y:
                    return (1,i)
    return (-1,-1)

def leaveMap(playerID,newMap):
    i = playerIDToIndex(playerID)
    print "player " + str(playerID) + " is leaving to map " + str(newMap)
    if i > -1:

        scriptOverride = 0
        try:
            prepScript('leavemap')
            import script_leavemap
            reload(script_leavemap)
            if "leavemap" in dir(script_leavemap):
                sendVariablesToScript()
                scriptOverride = getattr(script_leavemap,'leavemap')(playerID,newMap)
                loadVariablesFromScript()
            loadScriptPackets()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            print 'leavemap script failed'

        if scriptOverride == 0 or newMap == -1:
            despawnMessage = despawnPlayer(playerID)
            #send despawn to everyone but me (i'm already leaving)
            sendToAllOnMap(despawnMessage,int(playerID))
        #if scriptOverride == 1 and newMap > -1:
            if newMap > -1:
                if mapData.has_key("shop_id"):
                    shopID = int(mapData["shop_id"])
                else:
                    shopID = -1
                if shopID > -1 and shopDB != None:
                    shopName = str(shopDB[shopID]["name"])
                    shopJoin = str(shopDB[shopID]["leave_say"])
                    if shopName != "" and shopJoin != "":
                        sendPacketToPlayer(genMessage(shopName + " says, '" + shopJoin + "'",1,'#d3d3d3'),playerID)

                playerData[i]["pos"]["map_id"] = newMap
            else:
                packetToSend = genMessage(str(playerData[i]["name"]) + " has left!",0,'#696969')
                sendToEveryoneOnline(packetToSend)
                if mapData != None and mapData["boot_map"]["map_id"] > -1:
                    playerData[i]["pos"]["map_id"] = mapData["boot_map"]["map_id"]
                    playerData[i]["pos"]["x"] = mapData["boot_map"]["x"]
                    playerData[i]["pos"]["y"] = mapData["boot_map"]["y"]
                PL.delete('p' + str(playerID) + '2M')
                accountData = json.loads(r.get("aD_" + str(playerID)))
                for SLOTID in range(3):
                    if playerData[i]["name"] == accountData["players"][SLOTID]["name"]:
                        accountData["players"][int(SLOTID)] = playerData[i]
                        print "Saving slot ID " + str(SLOTID)
                        break
                PL.set('aD_' + str(playerID),json.dumps(accountData))
            #lets save our player prior to leaving
            PL.set('pD_' + str(playerID),json.dumps(playerData[i]))
            #remove the player from this map
            PL.lrem('map' + str(mapID) + 'Players',0,str(playerID))

            if newMap == -1:
                while playerID in playerIDList:
                    playerIDList.remove(playerID)
                del playerData[i]
        if newMap > -1 and scriptOverride == 0:
            sendPacketToPlayer(genPlaySound(0),playerID)
            playerData[i]["pos"]["map_id"] = newMap
            #push the player onto the new map as a new player
            PL.rpush('map' + str(newMap) + 'NewPlayers',str(playerID))
            PL.rpush('mapWQ',str(newMap))
            PL.set("p" + str(playerID) + '2M',newMap)
    #pl.set('pD_' + str(playerIDList[i]),json.dumps(playerData[i]))

def playerMove(message,playerID):
    playerIndex = playerIDToIndex(playerID)
    if playerIndex == -1:
        print("uhh.. wtf? " + str(playerID) + " has no playerIndex???")
        return
    #send to everyone that you're moving
    if playerData[playerIndex]["pos"]["x"] != int(message["x"]) and playerData[playerIndex]["pos"]["y"] != int(message["y"]):
        sendPacketToPlayer(spawnCharacter(playerIndex,playerID),playerID)
    else:
        playerAccess = playerData[playerIndex]["access"]
        scriptOverride = 0
#        if 1 == 1:
        try:
            prepScript('playermove')
            import script_playermove
            reload(script_playermove)
            if "playermove" in dir(script_playermove):
                sendVariablesToScript()
                scriptOverride = getattr(script_playermove,'playermove')(playerID,int(message["x"]),int(message["y"]),int(message["dir"]),int(message["speed"]))
                print "script override from playermove:" + str(scriptOverride)
                loadVariablesFromScript()
            loadScriptPackets()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            print "playermove script failed!"
            pass
        if  scriptOverride == 1:
            sendPacketToPlayer(spawnCharacter(playerIndex,playerID),playerID)
            return
        playerData[playerIndex]["pos"]["x"] = int(message["x"])
        playerData[playerIndex]["pos"]["y"] = int(message["y"])
        playerData[playerIndex]["pos"]["dir"] = int(message["dir"])
        tmp_y = int(message["y"])
        tmp_x = int(message["x"])
    #sendToAllOnMap(json.dumps(dict(playerData[playerIndex], **{"type":110,"player_id":playerID})),playerID)
        pTileType = mapData["tiles"][tmp_y][tmp_x]["type"]
        pTileData = mapData["tiles"][tmp_y][tmp_x]["data"]
        message["type"] = 115
        message["player_id"] = int(playerID)
        sendToAllOnMap(json.dumps(message),playerID)
        if message["speed"] != 0:
            if message["dir"] == 3:
                tmp_y -= 1
            elif message["dir"] == 0:
                tmp_y += 1
            elif message["dir"] == 1:
                tmp_x -= 1
            elif message["dir"] == 2:
                tmp_x += 1
        if tmp_y < 0:
            if int(mapData["map_north_id"]) > -1:
                playerData[playerIndex]["pos"]["y"] = 11
                leaveMap(playerID,int(mapData["map_north_id"]))
            else:
                sendPacketToPlayer(spawnCharacter(playerIndex,playerID),playerID)
        elif tmp_x < 0:
            if int(mapData["map_west_id"]) > -1:
                playerData[playerIndex]["pos"]["x"] = 11
                leaveMap(playerID,int(mapData["map_west_id"]))
            else:
                sendPacketToPlayer(spawnCharacter(playerIndex,playerID),playerID)
        elif tmp_x > 11:
            if int(mapData["map_east_id"]) > -1:
                playerData[playerIndex]["pos"]["x"] = 0
                leaveMap(playerID,int(mapData["map_east_id"]))
            else:
                sendPacketToPlayer(spawnCharacter(playerIndex,playerID),playerID)
        elif tmp_y > 11:
            if int(mapData["map_south_id"]) > -1:
                playerData[playerIndex]["pos"]["y"] = 0
                leaveMap(playerID,int(mapData["map_south_id"]))
            else:
                sendPacketToPlayer(spawnCharacter(playerIndex,playerID),playerID)
        elif message["speed"] != 0:
            tileType = mapData["tiles"][tmp_x][tmp_y]["type"]
            tileData = mapData["tiles"][tmp_x][tmp_y]["data"]
            if (tileType == 3):
                playerData[playerIndex]["pos"]["x"] = tileData["x"]
                playerData[playerIndex]["pos"]["y"] = tileData["y"]
                if tileData["map_id"] != mapID:
                    leaveMap(playerID,int(tileData["map_id"]))
                else:
                    sendToAllOnMap(spawnCharacter(playerIndex,playerID))
            elif (tileType == 0 or tileType == 2 or (tileType >= 4 and tileType <= 9) or tileType == 17 or (tileType >= 10 and tileType <= 14) or (tileType == 15 and tileData["blocked"] == False) or (pTileType == 2 and list(map(pTileData.get,["block_south","block_west","block_east","block_north"]))[tmp_dir] == True)) or checkDoorOpen(tmp_x,tmp_y) or playerAccess > 2:
                if tileType == 9 and playerData[playerIndex]["vitals"]["hp"] > 0:
                    if openDoor(tmp_x,tmp_y):
                        sendToAllOnMap(genMapDoors())
                elif tileType == 10 and playerData[playerIndex]["vitals"]["hp"] > 0:
                    openX = tileData["x"]
                    openY = tileData["y"]
                    closeTime = tileData["cooldown"]
                    if openDoor(openX,openY,closeTime):
                        sendToAllOnMap(genMapDoors())
                elif tileType == 17:
                    playerData[playerIndex]["pos"]["x"] = int(tmp_x)
                    playerData[playerIndex]["pos"]["y"] = int(tmp_y)

                    if tileData["sprite"] > -1 and int(playerData[playerIndex]["swap_sprite"]) == -1:
                        playerData[playerIndex]["swap_sprite"] = playerData[playerIndex]["sprite"]
                        playerData[playerIndex]["sprite"] = int(tileData["sprite"])
                        sendToAllOnMap(spawnCharacter(int(playerIndex),int(playerID)))
                    elif tileData["sprite"] == -1 and int(playerData[playerIndex]["swap_sprite"]) > -1:
                        playerData[playerIndex]["sprite"] = playerData[playerIndex]["swap_sprite"]
                        playerData[playerIndex]["swap_sprite"] = -1
                        sendToAllOnMap(spawnCharacter(int(playerIndex),int(playerID)))

                playerData[playerIndex]["pos"]["x"] = int(tmp_x)
                playerData[playerIndex]["pos"]["y"] = int(tmp_y)
            else:
                print("tileType:" + str(tileType) + " pTileType:" + str(pTileType))
                print("tileData:" + str(tileData) + " pTileData:" + str(pTileData))
                print("PLAYER WALKING THROUGH WALLS?? RESET POS")
                sendPacketToPlayer(spawnCharacter(playerIndex,playerID),playerID)
    #playerData["pos"]["x"]

def loadMobDB():
    global mobDB
    global lastMobRefresh
    if mobDB == None or int(time.time()) > (lastMobRefresh + 30):
        print "loading mobDB"
        tmp = r.get('npcList')
        if tmp != None:
            mobDB = json.loads(tmp)
            lastMobRefresh = int(time.time())

def loadShopDB():
    global shopDB
    global lastShopRefresh
    if shopDB == None or int(time.time()) > (lastShopRefresh + 10):
        print "loading shopDB"
        tmp = r.get('shopList')
        if tmp != None:
            shopDB = json.loads(tmp)
            lastShopRefresh = int(time.time())

def loadProfessionDB():
    global professionDB
    global lastProfessionRefresh
    if professionDB == None or int(time.time()) > (lastProfessionRefresh + 10): 
        print "loading professionDB"
        tmp = r.get('professionList')
        if tmp != None:
            professionDB = json.loads(tmp)
            lastProfessionRefresh = int(time.time())


def loadItemDB():
    global itemDB
    global lastItemRefresh
    #We'll cache items for 5 minutes just because they shouldn't be changing types that much to really matter
    if itemDB == None or int(time.time()) > (lastItemRefresh + 30):
        print "loading itemDB"
        tmp = r.get('itemList')
        if tmp != None:
            itemDB = json.loads(tmp)
            lastItemRefresh = int(time.time())

def addMapItem(mapItem):
    global mapItems
    if mapItem.has_key('item_id') and mapItem.has_key('amount') and mapItem.has_key('x') and mapItem.has_key('y') and mapItem.has_key('amount'):
        for i in range(len(mapItems)):
            print "checking " + str(i) + " mapItems[i][\"item_id\"] = " + str(mapItems[i]["item_id"])
            if int(mapItems[i]["item_id"]) == -1:
                mapItems[i] = mapItem
                packet = {}
                packet["type"] = 112
                packet["map_id"] = mapID
                packet["slot_id"] = i
                packet["map_items"] = mapItem
                return json.dumps(packet)
    return None

def useItem(message,playerID):
    playerIndex = playerIDToIndex(playerID)
    if message.has_key('slot_id') and playerIndex > -1:
        loadItemDB()
        slotID = int(message["slot_id"])
        itemID = int(playerData[playerIndex]["inv"][slotID]["item_id"])
        if itemID > -1:
            itemType = itemDB[itemID]["type"]
            playerProfession = playerData[playerIndex]["profession_id"]
            reqProfession = itemDB[itemID]["prof_req_flags"]
            if professionCheck(reqProfession,playerProfession) == 0:
                sendPacketToPlayer(genMessage('You cannot use this item!',4,'#00ffff',False),playerID)
                return
            scriptOverride = 0
            try:
                prepScript('item')
                import script_item
                reload(script_item)
                if "useitem" in dir(script_item):
                    sendVariablesToScript()
                    scriptOverride = getattr(script_item,'useitem')(playerID,itemID,slotID,itemType)
                    print "script override from useItem:" + str(scriptOverride)
                    loadVariablesFromScript()
                loadScriptPackets()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                print 'use item script failed'
                pass

            if itemType > 0 and itemType < 6 or itemType == 11 and scriptOverride == 0:
                scriptOverride = 0
                try:
                    if "equipitem" in dir(script_item):
                        sendVariablesToScript()
                        scriptOverride = getattr(script_item,'equipitem')(playerID,itemID,slotID,itemType)
                        print "script override from equipItem:" + str(scriptOverride)
                        loadVariablesFromScript()
                    loadScriptPackets()
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                    print 'equip item failed'
                    pass
                if scriptOverride == 0:
                    newInvSlot = itemType - 1
                    if newInvSlot == 10:
                        newInvSlot = 5
                    if newInvSlot == slotID:
                        #assume we're un-equpping then
                        for i in range(len(playerData[playerIndex]["inv"])):
                            if i > 5:
                                if playerData[playerIndex]["inv"][i]["item_id"] == -1:
                                    newInvSlot = i
                                    break
                    temp = deepcopy(playerData[playerIndex]["inv"][newInvSlot])
                    playerData[playerIndex]["inv"][newInvSlot] = deepcopy(playerData[playerIndex]["inv"][slotID])
                    playerData[playerIndex]["inv"][slotID] = deepcopy(temp)
                    packet = {}
                    packet["type"] = 119
                    packet["player_id"] = playerID
                    packet["slot_id"] = slotID
                    packet["inv"] = playerData[playerIndex]["inv"][slotID]
                    sendPacketToPlayer(json.dumps(packet),playerID)
                    packet["slot_id"] = newInvSlot
                    packet["inv"] = playerData[playerIndex]["inv"][newInvSlot]
                    sendPacketToPlayer(json.dumps(packet),playerID)
            if itemType == 8:
                pX = int(playerData[playerIndex]["pos"]["x"])
                pY = int(playerData[playerIndex]["pos"]["y"])
                d = int(playerData[playerIndex]["pos"]["dir"])
                cX,cY = [ (pX,pY + 1), (pX - 1,pY), (pX + 1, pY), (pX,pY - 1) ][d]
                if cX > -1 and cX < 12 and cY > -1 and cY < 12 and mapData["tiles"][cX][cY]["type"] == 9 and mapData["tiles"][cX][cY]["data"].has_key("item_id") and mapData["tiles"][cX][cY]["data"]["item_id"] == itemID:
                    if openDoor(cX,cY):
                        uses = playerData[playerIndex]["inv"][slotID]["uses"]
                        uses -= 1
                        if uses > 0:
                            playerData[playerIndex]["inv"][slotID]["uses"] = uses
                        else:
                            playerData[playerIndex]["inv"][slotID]["item_id"] = -1
                            playerData[playerIndex]["inv"][slotID]["uses"] = -1
                            playerData[playerIndex]["inv"][slotID]["amount"] = -1
                        sendPacketToPlayer(genInvUpdatePacket(playerID,slotID),playerID)
                        sendToAllOnMap(genMapDoors())

def genInvUpdatePacket(playerID,slotID):
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        packet = {}
        packet["type"] = 119
        packet["player_id"] = playerID
        packet["slot_id"] = slotID
        packet["inv"] = playerData[playerIndex]["inv"][slotID]
        return json.dumps(packet)

def dropItem(message,playerID):
    if message.has_key('slot_id') and message.has_key('amount'):
        playerIndex = playerIDToIndex(playerID)
        if int(playerIndex) == -1:
            print 'could not find player index; cannot drop an item'
            return
        if playerData[playerIndex]["vitals"]["hp"] == 0:
            return
        slotID = int(message["slot_id"])
        amount = int(message["amount"])
        print "itemID: " + str(int(playerData[playerIndex]["inv"][slotID]["item_id"])) + "  invAmount:" + str(int(playerData[playerIndex]["inv"][slotID]["amount"])) + ""
        itemID = int(playerData[playerIndex]["inv"][slotID]["item_id"])

        if itemID > -1:
            itemType = itemDB[itemID]["type"]
            scriptOverride = 0
            try:
                prepScript('item')
                import script_item
                reload(script_item)
                if "dropItem" in dir(script_item):
                    sendVariablesToScript()
                    scriptOverride = getattr(script_item,'dropItem')(playerID,itemID,slotID,amount,itemType)
                    print "script override from dropItem:" + str(scriptOverride)
                    loadVariablesFromScript()
                loadScriptPackets()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                print 'drop item script failed'
                pass
            if slotID > -1 and slotID < 30 and int(playerData[playerIndex]["inv"][slotID]["amount"]) >= amount and amount > 0 and scriptOverride == 0:
               print "dropping item..."
               mapItem = deepcopy(mapItemTemplate)
               mapItem["item_id"] = itemID
               mapItem["uses"] = int(playerData[playerIndex]["inv"][slotID]["uses"])
               mapItem["amount"] = int(amount)
               mapItem["x"] = playerData[playerIndex]["pos"]["x"]
               mapItem["y"] = playerData[playerIndex]["pos"]["y"]
               itemResult=addMapItem(mapItem)
               if itemResult != None:
                   sendToAllOnMap(itemResult)
                   newAmount = 0
                   newItemID = -1
                   if int(playerData[playerIndex]["inv"][slotID]["amount"]) > amount:
                       newAmount = int(playerData[playerIndex]["inv"][slotID]["amount"]) - amount
                       newItemID = int(playerData[playerIndex]["inv"][slotID]["item_id"])
        
                   playerData[playerIndex]["inv"][slotID]["item_id"] = newItemID
                   playerData[playerIndex]["inv"][slotID]["amount"] = newAmount
                   playerData[playerIndex]["inv"][slotID]["uses"] = 0
                   packet = {}
                   packet["type"] = 119
                   packet["player_id"] = playerID
                   packet["slot_id"] = slotID
                   packet["inv"] = playerData[playerIndex]["inv"][slotID]
                   sendPacketToPlayer(json.dumps(packet),playerID)

def handleTrade(message,playerID):
    playerIndex = playerIDToIndex(playerID)
    if playerIndex == -1 or playerData[playerIndex]["vitals"]["hp"] <= 0 or message.has_key('slot_id') == False or mapData.has_key('shop_id') == False:
        return
    loadShopDB()
    loadItemDB()
    shopID = mapData["shop_id"]
    shopSlot = message["slot_id"]
    if shopID > -1 and shopID < len(shopDB) and shopSlot > -1 and shopSlot < len(shopDB[shopID]["trades"]):
        takeItem = shopDB[shopID]["trades"][shopSlot]["take_item_id"]
        takeAmount = shopDB[shopID]["trades"][shopSlot]["take_amount"]
        giveItem = shopDB[shopID]["trades"][shopSlot]["give_item_id"]
        giveAmount = shopDB[shopID]["trades"][shopSlot]["give_amount"]
        shopTradeItem(playerID,takeItem,takeAmount,giveItem,giveAmount)

def handleSell(message,playerID):
    playerIndex = playerIDToIndex(playerID)
    if playerIndex == -1 or playerData[playerIndex]["vitals"]["hp"] <= 0 and message.has_key('slot_id'):
        return
    loadItemDB()
    shopID = mapData["shop_id"]
    slotID = message["slot_id"]
    if shopID > -1 and slotID > -1 and slotID < 30:
        itemID = playerData[playerIndex]["inv"][slotID]["item_id"]
        itemType = itemDB[itemID]["type"]
        itemUses = playerData[playerIndex]["inv"][slotID]["uses"]
        itemAmount = playerData[playerIndex]["inv"][slotID]["amount"]
        repairCost = int(itemDB[itemID]["repair_cost"])
        repairID = int(itemDB[itemID]["repair_id"])
        maxUses = int(itemDB[itemID]["uses"])
        print "selling:" + str(itemType) + " " + str(repairCost) + " " + str(repairID) + " " + str(maxUses)
        if (itemType > 0 and itemType < 6 or itemType == 11) and repairCost > 0 and repairID > 0 and maxUses > 0:
            print "selling item.."
            saleValue = int(float(float(repairCost) / float(maxUses)) * itemUses)
            if itemType == 11:
                saleValue = int(saleValue / 8)
            if shopTradeItem(playerID,itemID,itemAmount,repairID,saleValue,slotID) == True:
                sendPacketToPlayer(genWindow('winRecycle'),playerID)

def handleRepair(message,playerID):
    playerIndex = playerIDToIndex(playerID)
    if playerIndex == -1:
        return
    if message.has_key('slot_id'):
        slotID = message["slot_id"]
        repairItem(playerID,slotID)
    else:
        for i in range(len(playerData[playerIndex]["inv"])):
            repairItem(playerID,i)
    sendPacketToPlayer(genWindow('winRepair'),playerID)


def repairItem(playerID,slotID):
    playerIndex = playerIDToIndex(playerID)

    if playerID > -1 and playerIndex > -1 and slotID > -1 and slotID < 30:
        itemID = playerData[playerIndex]["inv"][slotID]["item_id"]
        itemType = itemDB[itemID]["type"]
        itemUses = playerData[playerIndex]["inv"][slotID]["uses"]
        itemAmount = playerData[playerIndex]["inv"][slotID]["amount"]
        repairCost = int(itemDB[itemID]["repair_cost"])
        repairID = int(itemDB[itemID]["repair_id"])
        maxUses = int(itemDB[itemID]["uses"])
        invSlot = getInvSlot(playerIndex,repairID)
        if invSlot > -1 and repairID > -1 and repairCost > 0 and int(playerData[playerIndex]["inv"][invSlot]["item_id"]) == repairID:
            currencyAmount = int(playerData[playerIndex]["inv"][invSlot]["amount"])
            if maxUses > itemUses:
                repairValue = int(float(float(repairCost) / float(maxUses)) * (maxUses - itemUses))
                if currencyAmount > repairValue:
                    currencyAmount -= repairValue
                    playerData[playerIndex]["inv"][slotID]["uses"] = maxUses
                elif currencyAmount <= repairValue:
                    eachUseCost = (float(repairCost) / float(maxUses))
                    repairedAmount = int(currencyAmount / eachUseCost)
                    currencyAmount -= int(eachUseCost * repairedAmount)
                    playerData[playerIndex]["inv"][slotID]["uses"] = int(itemUses + repairedAmount)
                if currencyAmount > 0:
                    playerData[playerIndex]["inv"][invSlot]["amount"] = currencyAmount
                elif currencyAmount == 0:
                    playerData[playerIndex]["inv"][invSlot]["amount"] = 0
                    playerData[playerIndex]["inv"][invSlot]["item_id"] = -1
                    playerData[playerIndex]["inv"][invSlot]["uses"] = 0
                else:
                    print "ohshit, negative currency amount (" + str(currencyAmount) + ")!!!"
            sendPacketToPlayer(genInvUpdatePacket(playerID,invSlot),playerID)
            sendPacketToPlayer(genInvUpdatePacket(playerID,slotID),playerID)
                

def getInvSlot(playerIndex,itemID):
    for invSlot in range(len(playerData[playerIndex]["inv"])):
        if int(playerData[playerIndex]["inv"][invSlot]["item_id"]) == itemID:
            return invSlot
    return -1

def shopTradeItem(playerID,requestedItem,requestedAmount,grantedItem,grantedAmount,requestedItemSlot = -1,grantedItemSlot = -1):
    playerIndex = playerIDToIndex(playerID)
    if playerIndex == -1 or playerData[playerIndex]["vitals"]["hp"] <= 0:
        return
    
    #requestedItemSlot = -1
    #grantedItemSlot = -1
    grantedItemType = int(itemDB[grantedItem]["type"])
    print "requestedItem:" + str(requestedItem)
    print "grantedItem:" + str(grantedItem)
    for invID in range(len(playerData[playerIndex]["inv"])):
        if int(playerData[playerIndex]["inv"][invID]["item_id"]) == requestedItem and requestedItemSlot == -1:
            if int(playerData[playerIndex]["inv"][invID]["amount"]) >= requestedAmount:
                requestedItemSlot = invID
            else:
                return False
        if ((grantedItemType == 0 or grantedItemType == 6) and int(playerData[playerIndex]["inv"][invID]["item_id"]) == grantedItem):
            grantedItemSlot = invID
        elif int(playerData[playerIndex]["inv"][invID]["item_id"]) == -1 and grantedItemSlot == -1 and invID > 5:
            grantedItemSlot = invID
    if grantedItemSlot > -1 and requestedItemSlot > -1:
        print "grantedItemSlot:" + str(grantedItemSlot) + " requestedItemSlot:" + str(requestedItemSlot)
        newAmount = int(playerData[playerIndex]["inv"][requestedItemSlot]["amount"]) - requestedAmount
        if newAmount < 0:
            print "WTF how did we get here??"
            return False
        elif newAmount == 0:
            playerData[playerIndex]["inv"][requestedItemSlot]["amount"] = 0
            playerData[playerIndex]["inv"][requestedItemSlot]["uses"] = 0
            playerData[playerIndex]["inv"][requestedItemSlot]["item_id"] = -1
        elif newAmount > 0:
            playerData[playerIndex]["inv"][requestedItemSlot]["amount"] = newAmount

        if int(playerData[playerIndex]["inv"][grantedItemSlot]["item_id"]) == -1:
            playerData[playerIndex]["inv"][grantedItemSlot]["amount"] = grantedAmount
            playerData[playerIndex]["inv"][grantedItemSlot]["uses"] = int(itemDB[grantedItem]["uses"])
            playerData[playerIndex]["inv"][grantedItemSlot]["item_id"] = grantedItem
        else:
            playerData[playerIndex]["inv"][grantedItemSlot]["amount"] = int(playerData[playerIndex]["inv"][grantedItemSlot]["amount"]) + grantedAmount
        sendPacketToPlayer(genInvUpdatePacket(playerID,grantedItemSlot),playerID)
        sendPacketToPlayer(genInvUpdatePacket(playerID,requestedItemSlot),playerID)
        return True

def pickupItem(message,playerID):
    playerIndex = playerIDToIndex(playerID)
    if playerIndex == -1:
        return
    if playerData[playerIndex]["vitals"]["hp"] <= 0:
        if playerData[playerIndex]["data"].has_key("dead") == True and int(playerData[playerIndex]["data"]["dead"] + 2) <= time.time():
            playerData[playerIndex]["vitals"]["hp"] = 1
            playerData[playerIndex]["pos"]["x"] = 2
            playerData[playerIndex]["pos"]["y"] = 7
            leaveMap(playerID,7)
        return
        
    slotID = -1
    donePickup = 0
    loadItemDB()
    freeSlotID = -1
    for i in range(len(playerData[playerIndex]["inv"])):
        if i > 5:
            print playerData[playerIndex]["inv"]
            if int(playerData[playerIndex]["inv"][i]["item_id"]) == -1:
                freeSlotID = i
                break
    slotID = freeSlotID
    for i in range(len(mapItems)):
        if int(mapItems[i]["item_id"]) > 0 and int(mapItems[i]["x"]) == int(playerData[playerIndex]["pos"]["x"]) and int(mapItems[i]["y"]) == int(playerData[playerIndex]["pos"]["y"]):
        

            tileStr = str(str(mapItems[i]["x"]) + ":" + str(mapItems[i]["y"]))
            #players
            if mapMeta.has_key("spawnItems") == True and mapMeta["spawnItems"].has_key(tileStr) == True and mapData.has_key("treasure") and mapData["treasure"] == True:
                if mapMeta["spawnItems"][tileStr]["mapItemSlot"] == i:
                    if mapMeta["players"].has_key(str(playerID)) == False:
                        mapMeta["players"][str(playerID)] = {}
                    if mapMeta["players"][str(playerID)].has_key(str("collected" + tileStr)):
                        sendPacketToPlayer(genMessage('You have already picked up this item',4,'#ff0000',False),playerID)
                        return
                        #mapMeta["spawnItems"][tileStr]["mapItemSlot"] = -1
                        #mapMeta["spawnItems"][tileStr]["itemRespawn"] = int(time.time())

            itemID = int(mapItems[i]["item_id"])
            print("item to pickup is type:" + str(itemDB[itemID]["type"]))
            if int(itemDB[itemID]["type"]) == 0 or int(itemDB[itemID]["type"]) == 6:
                for invID in range(len(playerData[playerIndex]["inv"])):
                    
                    print("inventory slot[" + str(invID) + "] item_id[" + str(playerData[playerIndex]["inv"][invID]["item_id"]) + "]")
                    if int(playerData[playerIndex]["inv"][invID]["item_id"]) == itemID:
                        print("inventory slot[" + str(invID) + "] matched!")
                        itemLimit = int(itemDB[itemID]["limit"])
                        playerAmount = int(playerData[playerIndex]["inv"][invID]["amount"])
                        if itemLimit == 0 or playerAmount < itemLimit:
                            print("itemlimit and playeramount are good")
                            pickupAmount = mapItems[i]["amount"]
                            
                            if itemLimit == 0 or int(pickupAmount + playerAmount) <= itemLimit:
                                playerData[playerIndex]["inv"][invID]["amount"] = int(playerAmount + pickupAmount)
                                mapItems[i]["amount"] = 0
                                mapItems[i]["item_id"] = -1
                                mapItems[i]["uses"] = 0
                            else:
                                mapItems[i]["amount"] -= int(itemLimit - playerAmount)
                                playerData[playerIndex]["inv"][invID]["amount"] = itemLimit
                            donePickup = 1
                            slotID = invID
                            break
            if slotID > -1:
                if donePickup == 0:
                    playerData[playerIndex]["inv"][slotID]["item_id"] = mapItems[i]["item_id"]
                    playerData[playerIndex]["inv"][slotID]["amount"] = mapItems[i]["amount"]
                    playerData[playerIndex]["inv"][slotID]["uses"] = mapItems[i]["uses"]
                    mapItems[i] = deepcopy(mapItemTemplate)
                packet = {}
                packet["type"] = 112
                packet["slot_id"] = i
                packet["map_items"] = mapItems[i]
                #packet["map_items"]["item_id"] = -1
                packet["map_id"] = mapID
                sendToAllOnMap(json.dumps(packet))
                packet = {}
                packet["type"] = 119
                packet["player_id"] = playerID
                packet["slot_id"] = slotID
                packet["inv"] = playerData[playerIndex]["inv"][slotID]
                #packet["amount"] = playerData[playerIndex]["inv"][str(slotID)]["amount"]
                #packet["uses"] = playerData[playerIndex]["inv"][str(slotID)]["uses"]
                if mapMeta.has_key("spawnItems") == True and mapMeta["spawnItems"].has_key(tileStr) == True and mapData.has_key('treasure') and mapData["treasure"] == True:
                    if mapMeta["spawnItems"][tileStr]["mapItemSlot"] == i:
                        if mapMeta["players"][str(playerID)].has_key(str("collected" + tileStr)) == False:
                            mapMeta["spawnItems"][tileStr]["mapItemSlot"] = -1
                            mapMeta["spawnItems"][tileStr]["itemRespawn"] = int(time.time())
                            mapMeta["players"][str(playerID)][str("collected" + tileStr)] = 1
                elif mapMeta.has_key("spawnItems") == True and mapMeta["spawnItems"].has_key(tileStr) == True:
                    mapMeta["spawnItems"][tileStr]["mapItemSlot"] = -1
                    mapMeta["spawnItems"][tileStr]["itemRespawn"] = int(time.time())


                sendPacketToPlayer(json.dumps(packet),playerID)
            else:
                sendPacketToPlayer(genMessage('You cannot carry anymore!',4,'#ff0000',True),playerID)
            return
    sendPacketToPlayer(genMessage('nothing to pickup!',4,'#ff0000',True),playerID)


def genMessage(text,channel_id = 0,color = '#ff00ff',temp = False):
    packet = {}
    packet["type"] = 114
    packet["channel_id"] = channel_id
    packet["color"] = color #"#ff00ff"
    packet["temp"] = temp
    packet["text"] = str(text)
    return json.dumps(packet)

def saveScript(message,playerID):
    playerIndex = playerIDToIndex(playerID)

    if playerData[playerIndex]["access"] > 3:
        scriptName = message["name"]
        scriptText = message["script"]
        playerIndex = playerIDToIndex(playerID)
        PL.set('script_' + str(scriptName),scriptText)
        sendPacketToPlayer(genWindow('winGame'),playerID)

def editScript(name):
    scriptText = r.get("script_" + str(name))
    if scriptText == None:
        scriptText = ''
    packet = {}
    packet["type"] = 138
    packet["script"] = scriptText
    packet["name"] = str(name)
    return json.dumps(packet)

def getPlayerID(playerName):
    for i in range(len(playerIDList)):
        if playerData[i]["name"].lower() == playerName.lower():
            return playerIDList[i]
    return -1

def parseChat(rawPacket,playerID):
    chatMessage = rawPacket["text"]
    playerIndex = playerIDToIndex(playerID)
    if playerIndex == -1:
        print("playerID to index returned -1 for some reason for playerID " + str(playerID))
        return
    if chatMessage.lower() == "/editmap" and playerData[playerIndex]["access"] > 0:
        sendPacketToPlayer(genWindow('winMapProperties'),playerID)
    elif "/copymap " in chatMessage.lower() and playerData[playerIndex]["access"] > 0:
        tmp = chatMessage.split(' ')
        if len(tmp) == 2:
            try:
                tmpData = r.get('map' + str(tmp[1]) + 'Data')
                if tmpData != None:
                    sendPacketToPlayer('{"type":106,"map_id":' + str(mapID) + ',"map":' + tmpData + '}',int(playerID))
                    for i in range(len(playerIDList)):
                        sendPacketToPlayer(spawnCharacter(int(i)),int(playerID))

                    sendPacketToPlayer(genMessage('Map ' + str(tmp[1]) + ' has been sent to only you.',0,'#ff0000'),playerID)
                else:
                    sendPacketToPlayer(genMessage('Could not load map ' + str(tmp[1]),0,'#ff0000'),playerID)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                print 'copymap failed'                
                pass
    elif "/setsprite " in chatMessage.lower() and playerData[playerIndex]["access"] > 0:
       tmp = chatMessage.split(' ')
       if len(tmp) == 2:
           try:
               playerData[playerIndex]["sprite"] = int(tmp[1])
               sendToAllOnMap(spawnCharacter(int(playerIndex),int(playerID)))
           except:
               pass
    elif ( "/setcolor " in chatMessage.lower() or "/setcolour " in chatMessage.lower() ) and playerData[playerIndex]["access"] > 0:
        tmp = chatMessage.split(' ')
        if len(tmp) == 2:
           try:
               playerData[playerIndex]["color"] = str(tmp[1])
               sendToAllOnMap(spawnCharacter(int(playerIndex),int(playerID)))
           except:
               pass
    elif chatMessage.lower() == "/who":
        loadProfessionDB()
        #ugh, i hate this; need to figure out a better way
        playerList = ''
        classes = {}
        temp_pl = r.pipeline()
        count = 0
        for key in r.keys('p*2M'):
            PID=str(key[1:])[:-2]
            temp_pl.get('pD_' + str(PID))
        results = temp_pl.execute()
        for i in range(len(results)):
            if results[i] != None:
                count += 1
                tmpPlayer=json.loads(results[i])
                playerList = str(playerList) + str(tmpPlayer["name"]) + ' [lv ' + str(tmpPlayer["level"]) + '], '
                if classes.has_key(str(tmpPlayer["profession_id"])) == False:
                    classes[str(tmpPlayer["profession_id"])] = str(tmpPlayer["name"]) + ', '
                else:
                    classes[str(tmpPlayer["profession_id"])] = str(classes[str(tmpPlayer["profession_id"])]) + str(tmpPlayer["name"]) + ', '
        sendPacketToPlayer(genMessage( str(count) + " players Online: " + playerList[:-2]  ,0,'#ffff00'),playerID)
        for profID in classes:
            if professionDB[int(profID)]["name"] != '':
                sendPacketToPlayer(genMessage(professionDB[int(profID)]["name"] + "s: " + str(classes[profID])[:-2],0,'#ffff00'),playerID)
    elif "/warpto " in chatMessage.lower() and playerData[playerIndex]["access"] > 0:
        warpingTo = chatMessage.lower()[8:]
        temp_pl = r.pipeline()
        for key in r.keys('p*2M'):
            PID=str(key[1:])[:-2]
            temp_pl.get('pD_' + str(PID))
        results = temp_pl.execute()
        for i in range(len(results)):
            if results[i] != None:
                tmpPlayer=json.loads(results[i])
                if tmpPlayer["name"].lower() == warpingTo:
                    playerData[playerIndex]["pos"]["x"] = tmpPlayer["pos"]["x"]
                    playerData[playerIndex]["pos"]["y"] = tmpPlayer["pos"]["y"]
                    if playerData[playerIndex]["pos"]["map_id"] != tmpPlayer["pos"]["map_id"]:
                        leaveMap(playerID,int(tmpPlayer["pos"]["map_id"]))
                    break
    elif "/setaccess " in chatMessage.lower() and playerData[playerIndex]["access"] > 3:
        try:
            tmp = chatMessage.split(" ")
            if len(tmp) == 3:
                targetID = getPlayerID(tmp[1])
                targetAccess = int(tmp[2])
                if targetID > -1:
                    targetIndex = playerIDToIndex(targetID)
                    playerData[targetIndex]["access"] = targetAccess
                    sendPacketToPlayer(genMessage('Set ' + str(tmp[1]) + "'s access to " + str(targetAccess),0,'#0000ff'),playerID)
                    sendPacketToPlayer(reloadCharacterPacket(targetIndex),targetID)
                    sendPacketToPlayer(genWindow('winGame'),targetID)
        except:
            pass
    elif chatMessage.lower() == "/editprofession" and playerData[playerIndex]["access"] > 0:
        sendPacketToPlayer(genWindow('winProfessionEditor'),playerID)
    elif chatMessage.lower() == "/editshop" and playerData[playerIndex]["access"] > 0:
        sendPacketToPlayer(genWindow('winShopEditor'),playerID)
    elif chatMessage.lower() == "/edititem" and playerData[playerIndex]["access"] > 0:
        sendPacketToPlayer(genWindow('winItemEditor'),playerID)
    elif chatMessage.lower() == "/editnpc" and playerData[playerIndex]["access"] > 0:
        sendPacketToPlayer(genWindow('winNPCEditor'),playerID)
    elif "/editscript " in chatMessage.lower() and playerData[playerIndex]["access"] > 1:
        tmp = chatMessage.split(" ")
        if len(tmp) == 2:
            sendPacketToPlayer(editScript(tmp[1]),playerID)
            sendPacketToPlayer(genWindow('winScriptEditor'),playerID)
    elif "/provoke " in chatMessage.lower() and playerData[playerIndex]["access"] > 0:
        try:
            tmp = chatMessage.split(" ")
            if len(tmp) == 2:
                aggroAmount = int(tmp[1])
                for i in range(len(mapNPCs)):
                    if int(mapNPCs[i]["npc_id"]) > -1 and mapNPCs[i]["vitals"]["hp"] > 0:
                        if aggroAmount == 0:
                            del mapMeta["mobs"][i]["aggroList"][str(playerID)]
                        else:
                            mapMeta["mobs"][i]["aggroList"][str(playerID)] = aggroAmount
        except:
            pass
    elif "/spawnitem " in chatMessage.lower() and playerData[playerIndex]["access"] > 0:
        try:
            tmp=chatMessage.split(" ")
            if len(tmp) == 4 and tmp[1] != '' and tmp[2] != '' and tmp[3] != '':
               mapItem = deepcopy(mapItemTemplate)
               mapItem["item_id"] = int(tmp[1])
               mapItem["uses"] = int(tmp[2])
               mapItem["amount"] = int(tmp[3])
               mapItem["x"] = playerData[playerIndex]["pos"]["x"]
               mapItem["y"] = playerData[playerIndex]["pos"]["y"]
               itemResult=addMapItem(mapItem)
               if itemResult != None:
                   sendToAllOnMap(itemResult)
               else:
                   sendPacketToPlayer(genMessage('Map is full, cannot spawn anymore!'),playerID)
        except:
            pass
    elif chatMessage[0] == "'":
        packetToSend = genMessage(str(playerData[playerIndex]["name"]) + ":" + str(chatMessage[1:]),0,'#ff00ff')
        sendToEveryoneOnline(packetToSend)
    elif chatMessage[0] == "@":
        tmp=chatMessage.split(" ")
        msg = " ".join(tmp[1:])
        whisperTo = tmp[0][1:]
        targetID = getPlayerID(tmp[0][1:])
        messageToSender = genMessage(">>" + str(tmp[0][1:]) + ": " + str(msg),0,'#00ff00')
        messageToSend = genMessage(str(playerData[playerIndex]["name"]) + " >> " + str(msg),0,'#00ff00')
        sentMsg = 0
        if targetID > -1:
            #thank god, same map
            sendPacketToPlayer(messageToSend,targetID)
            sendPacketToPlayer(messageToSender,playerID)
            sentMsg = 1
        else:
            #FML; scan everyone....
            pidList = []
            temp_pl = r.pipeline()
            for key in r.keys('p*2M'): #r.scan_iter('p*2M'):
                PID=str(key[1:])[:-2]
                temp_pl.get('pD_' + str(PID))
                pidList.append(PID)
            results = temp_pl.execute()
            for i in range(len(results)):
                if results[i] != None:
                    tmpPlayer=json.loads(results[i])
                    if tmpPlayer["name"].lower() == whisperTo.lower():
                        tmp = r.get(str(pidList[i]) + "2SID")
                        if tmp != None:
                            connInfo = tmp.split(" ")
                            socketServer = connInfo[0]
                            socketID = connInfo[1]
                            PL.rpush("wsQ" + str(socketServer),str(socketID) + " " + str(messageToSend))
                            sendPacketToPlayer(messageToSender,playerID)
                            sentMsg = 1
                        break
        if sentMsg == 0:
            sendPacketToPlayer(genMessage(str(tmp[0][1:]) + " is not logged on!",0,'#ff0000'),playerID)

    else:
        scriptOverride = 0
        try:
            prepScript('chat')
            import script_chat
            reload(script_chat)
            if "handleChat" in dir(script_chat):
                sendVariablesToScript()
                scriptOverride = getattr(script_chat,'handleChat')(playerID,str(chatMessage))
                print "script override from chat:" + str(scriptOverride)
                loadVariablesFromScript()
            loadScriptPackets()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            print "script_chat failed!"
            pass
        if scriptOverride == 0: 
            print("received message:" + str(chatMessage))
            sendToAllOnMap(genMessage(str(playerData[playerIndex]["name"]) + ":" + str(chatMessage),0,'#ffffff'))

def saveNPC(message,playerID):
    global lastMobRefresh
    global mobDB
    playerIndex = playerIDToIndex(playerID)
    if playerData[playerIndex]["access"] > 0:
        lastMobRefresh = 0
        loadMobDB()
        npc_id = int(message["npc_id"])
        mobDB[npc_id] = message["npc"]
        PL.set('npcList',json.dumps(mobDB))
        #sendPacketToPlayer(genWindow('winGame'),playerID)
        packet = {}
        packet["type"] = 104
        packet["npc"] = message["npc"]
        packet["npc_id"] = npc_id
        sendToEveryoneOnline(json.dumps(packet))

def saveShop(message,playerID):
    global lastShopRefresh
    global shopDB
    playerIndex = playerIDToIndex(playerID)
    if playerData[playerIndex]["access"] > 0:
        lastShopRefresh = 0
        loadShopDB()
        shop_id = int(message["shop_id"])
        shopDB[shop_id] = message["shop"]
        PL.set('shopList',json.dumps(shopDB))
        sendPacketToPlayer(genWindow('winGame'),playerID)
        packet = {}
        packet["type"] = 105
        packet["shop"] = message["shop"]
        packet["shop_id"] = shop_id
        sendToEveryoneOnline(json.dumps(packet))


def saveItem(message, playerID):
    global lastItemRefresh
    global itemDB
    playerIndex = playerIDToIndex(playerID)
    if playerData[playerIndex]["access"] > 0:
        #force refresh
        lastItemRefresh = 0
        loadItemDB()
        itemSlot = int(message["item_id"])
        itemDB[int(itemSlot)] = message["item"]
        packet = {}
        packet["type"] = 103
        packet["item"] = message["item"]
        packet["item_id"] = int(message["item_id"])
        PL.set('itemList',json.dumps(itemDB))
        sendToEveryoneOnline(json.dumps(packet))
        #sendPacketToPlayer(genWindow('winGame'),playerID)


def saveProfession(message,playerID):
    global lastProfessionRefresh
    global professionDB
    playerIndex = playerIDToIndex(playerID)
    if playerData[playerIndex]["access"] > 0:
        #force refresh
        lastProfessionRefresh = 0
        loadProfessionDB()
        professionSlot = int(message["profession_id"])
        professionDB[int(professionSlot)] = message["profession"]
        packet = {}
        packet["type"] = 102
        packet["profession"] = message["profession"]
        packet["profession_id"] = int(message["profession_id"])
        PL.set('professionList',json.dumps(professionDB))
        sendToEveryoneOnline(json.dumps(packet))
        sendPacketToPlayer(genWindow('winGame'),playerID)


def sendToEveryoneOnline(packetToSend):
    for key in r.scan_iter('p*2M'):
        PID=str(key[1:])[:-2]
        print("key:" + str(key) + " PID:" + str(PID))
        sessionID=r.get(str(PID) + '2SID')
        if sessionID != None:
            print("sending to PID:" + str(PID) + " session(" + str(sessionID) + ")")
            connInfo = sessionID.split(" ")
            socketServer = connInfo[0]
            socketID = connInfo[1]
            PL.rpush("wsQ" + str(socketServer),str(socketID) + " " + str(packetToSend))

def validMobSquare(tileType,pTileData):
#    print ("valid mob square? tileType:" + str(tileType) + " pTileData:" + str(pTileData))
    if (tileType == 0 or tileType == 2 or (tileType >= 4 and tileType <= 7 and tileType != 6) or tileType == 17 or tileType == 10 or tileType == 11 or tileType == 20 or (tileType == 15 and pTileData["blocked"] == False)):
        return True
    else:
        return False

def tileFree(x,y):
    for i in range(len(mapNPCs)):
        if int(mapNPCs[i]["npc_id"]) > -1 and mapNPCs[i]["vitals"]["hp"] > 0:
            if mapNPCs[i]["pos"]["x"] == x and mapNPCs[i]["pos"]["y"] == y:
                return False
    for i in range(len(playerData)):
        if playerData[i]["vitals"]["hp"] > 0:
            if playerData[i]["pos"]["x"] == x and playerData[i]["pos"]["y"] == y:
                return False
    return True

def mobAStar(mapTile,startp,endp):

    w,h = 12,12
    sx,sy = startp
    ex,ey = endp
    print("sx:" + str(sx) + " sy:" + str(sy) + " ex:" + str(ex) + " ey:" + str(ey))
    #[parent node, x, y,g,f]
    node = [None,sx,sy,0,abs(ex-sx)+abs(ey-sy)]
    closeList = [node]
    createdList = {}
    createdList[sy*w+sx] = node
    k=0

    while(closeList):
        node = closeList.pop(0)
        x = node[1]
        y = node[2]
        l = node[3]+1
        k+=1
        #find neighbours
        #make the path not too strange
        if k&1:
            neighbours = ((x,y+1,0),(x,y-1,3),(x+1,y,2),(x-1,y,1))
        else:
            neighbours = ((x+1,y,2),(x-1,y,1),(x,y+1,0),(x,y-1,3))
        for nx,ny,d in neighbours:
            #print "ASTAR: " + str(nx) + " " + str(ny) + " " + str(d) + " h=" + str(h) + " w=" + str(w)
            if nx==ex and ny==ey and not ((mapTile[x][y]["type"]==2 and list(map(mapTile[x][y]["data"].get,["block_south","block_west","block_east","block_north"]))[d] == True) or (mapTile[x][y]["type"]==9 and list(map(mapTile[x][y]["data"].get,["lock_south","lock_west","lock_east","lock_north"]))[d] == True)):
                path = [(ex,ey)]
                while node:
                    path.append((node[1],node[2]))
                    node = node[0]
                return list(reversed(path))
            if 0<=nx<w and 0<=ny<h:
                if (mapTile[nx][ny]["type"]==0 or mapTile[nx][ny]["type"]==2 or (mapTile[nx][ny]["type"] >= 4 and mapTile[nx][ny]["type"] <= 7) or mapTile[nx][ny]["type"] == 17 or mapTile[nx][ny]["type"] == 20 or (mapTile[nx][ny]["type"] >= 10 and mapTile[nx][ny]["type"] <= 14) or (mapTile[nx][ny]["type"]==15 and mapTile[nx][ny]["data"]["blocked"] == False) or (mapTile[nx][ny]["type"]==9 and list(map(mapTile[nx][ny]["data"].get,["lock_south","lock_west","lock_east","lock_north"]))[d] == False)) and not ((mapTile[x][y]["type"]==2 and list(map(mapTile[x][y]["data"].get,["block_south","block_west","block_east","block_north"]))[d] == True) or (mapTile[x][y]["type"]==9 and list(map(mapTile[x][y]["data"].get,["lock_south","lock_west","lock_east","lock_north"]))[d] == True) or checkDoorOpen(nx,ny) == True) and tileFree(nx,ny) == True:
                    if ny*w+nx not in createdList:
                        nn = (node,nx,ny,l,l+abs(nx-ex)+abs(ny-ey))
                        createdList[ny*w+nx] = nn
                        #adding to closelist ,using binary heap
                        nni = len(closeList)
                        closeList.append(nn)
                        while nni:
                            i = (nni-1)>>1
                            if closeList[i][4]>nn[4]:
                                closeList[i],closeList[nni] = nn,closeList[i]
                                nni = i
                            else:
                                break

    return 'NF'


def genNPCUpdate(npcToUpdate,npcSlotID):
    packet = {}
    packet["type"] = 113
    packet["slot_id"] = npcSlotID
    packet["map_npcs"] = npcToUpdate
    packet["map_id"] = int(mapID)
    print("gen NPC Update called... should send " + json.dumps(packet))
    return json.dumps(packet)

def genAllNPCUpdate():
    global mapNPCs
    packet = {}
    packet["type"] = 113
    packet["map_npcs"] = mapNPCs
    packet["map_id"] = int(mapID)
    return json.dumps(packet)

def checkDirFace(myX, myY, lookX,lookY,curD):
    if lookX > myX and curD != 2:
        return 2
    elif lookX < myX and curD != 1:
        return 1
    elif lookY > myY and curD != 0:
        return 0
    elif lookY < myY and curD != 3:
        return 3
    else:
        return -1

def moveNPCTo(mapNPCID,x,y,speed):
    start_x=mapNPCs[mapNPCID]["pos"]["x"]
    start_y=mapNPCs[mapNPCID]["pos"]["y"]
    packet = {}
    packet["type"] = 118
    packet["x"] = start_x
    packet["y"] = start_y
    packet["speed"] = speed
    packet["slot_id"] = mapNPCID
    packet["map_id"] = int(mapID)
    d = checkDirFace(start_x,start_y,x,y,-1)
    if d == -1:
        d = mapNPCs[mapNPCID]["pos"]["dir"]
        if d == -1:
            d = 0
    packet["dir"] = d
    if speed > 0:
        mapNPCs[mapNPCID]["pos"]["x"] = x
        mapNPCs[mapNPCID]["pos"]["y"] = y
        mapNPCs[mapNPCID]["pos"]["dir"] = d
    else:
        mapNPCs[mapNPCID]["pos"]["dir"] = d
    return json.dumps(packet)

def genPlaySound(sound_id):
    packet = {}
    packet["type"] = 123
    packet["sound_id"] = sound_id
    return json.dumps(packet)

def hitMob(playerID,mapNPCID,damage):
   return 

def handleNPCDeath(i):
    global mapNPCs
    global mobDB
    loadMobDB()
    loadItemDB()

    npc_id = mapNPCs[i]["npc_id"]
    scriptOverride = 0
    curTime = int(time.time() * 1000)
    try:
        prepScript('mobdeath')
        import script_mobdeath
        reload(script_mobdeath)
        if str("mobdeath_" + str(mapNPCs[i]["npc_id"])) in dir(script_mobdeath):
            sendVariablesToScript()
            scriptOverride = getattr(script_mobdeath,'mobdeath_' + str(str(mapNPCs[i]["npc_id"])))(i)
            loadVariablesFromScript()
            print "script Override from death:" + str(scriptOverride)
        elif "genericdeath" in dir(script_mobdeath):
            sendVariablesToScript()          
            scriptOverride = getattr(script_mobdeath,'genericdeath')(i)
            loadVariablesFromScript()
        loadScriptPackets()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        print "mobdeath Failed!"
        pass

    if scriptOverride == 0:
        expSplit = 0
        expDistribution = 0
        expSplitPIDList = []
        for pID in mapMeta["mobs"][i]["aggroList"]:
            pIndex = playerIDToIndex(pID)
            if mapMeta["mobs"][i]["aggroList"][str(pID)] > 1 and pIndex > -1:
                expSplit += 1
                expSplitPIDList.append(pIndex)
        if mobDB[npc_id]["stats"]["spd"] < 0:
            expDistribution -= int(mobDB[npc_id]["stats"]["spd"])
        else:
            mobSTR = int(mobDB[npc_id]["stats"]["str"]) * 0.5
            mobDEF = int(mobDB[npc_id]["stats"]["def"])
            mobHP = int(mobDB[npc_id]["vitals"]["hp"])
            expDistribution = int((mobSTR * 10) + (10 * mobDEF) + (mobHP * ((mobSTR / 6) + (mobDEF / 6))))
        if expSplit > 1:
            expDistribution *= 1.2
        else:
            expSplit = 1
        expDistribution = int(expDistribution / expSplit)
        for x in range(len(expSplitPIDList)):
            playerData[expSplitPIDList[x]]["exp"] += expDistribution
            sendPacketToPlayer(genExpMessage(int(playerIDList[expSplitPIDList[x]]),playerData[expSplitPIDList[x]]["exp"]),playerIDList[expSplitPIDList[x]])
            sendPacketToPlayer(genMessage("You have gained " + str(expDistribution) + " experience points for defeating the " + str(mobDB[npc_id]["name"]) + ".",0,'#ffff00',True),playerIDList[expSplitPIDList[x]])
        if mapMeta["mobs"][i].has_key('data'):
            #clear all npc flags
            del mapMeta["mobs"][i]["data"]
        mapMeta["mobs"][i]["respawnTime"] = curTime + (int(mobDB[npc_id]["spawn_delay"]) * 1000)
        mapNPCs[i]["npc_id"] = -1
        sendToAllOnMap(genNPCUpdate(mapNPCs[i],i))
        sendToAllOnMap(genPlaySound(2))
        mapMeta["mobs"][i]["tileSpawned"] = ''
        for drops in range(len(mobDB[npc_id]["drop_items"])):
            chance = mobDB[npc_id]["drop_items"][drops]["chance"]
            if int(random.randint(1,100)) <= chance:
                mapItem = deepcopy(mapItemTemplate)
                itemID = int(mobDB[npc_id]["drop_items"][drops]["item_id"])
                mapItem["item_id"] = itemID
                mapItem["uses"] = itemDB[itemID]["uses"]
                mapItem["amount"] = int(mobDB[npc_id]["drop_items"][drops]["amount"])
                if int(mapItem["amount"]) == 0:
                    mapItem["amount"] = 1
                mapItem["x"] = mapNPCs[i]["pos"]["x"]
                mapItem["y"] = mapNPCs[i]["pos"]["y"]
                itemResult=addMapItem(mapItem)
                if itemResult != None:
                    sendToAllOnMap(itemResult)


def genExpMessage(playerID,exp):
    packet = {}
    packet["type"] = 137
    packet["player_id"] = playerID
    packet["exp"] = exp
    return json.dumps(packet)

def expRequiredForLevel(level):
    return int(1000 * (int(level) ** (1 + 0.01 * int(level))))

def handleLevelUp(playerIndex):
    global playerData
    playerID = playerIDList[playerIndex]
    scriptOverride = 0
    curTime = int(time.time() * 1000)
    playerLevel = int(playerData[playerIndex]["level"])
    try:
        prepScript('playerlevel')
        import script_playerlevel
        reload(script_playerlevel)
        if "levelup" in dir(script_playerlevel):
            sendVariablesToScript()
            scriptOverride = getattr(script_playerlevel,'levelup')(playerIndex,playerLevel)
            loadVariablesFromScript()
            loadScriptPackets()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        print "playerlevel Failed!"
        pass
    if scriptOverride == 0:
        playerData[playerIndex]["exp"] = int(playerData[playerIndex]["exp"]) - expRequiredForLevel(playerLevel)
        playerData[playerIndex]["level"] = playerLevel + 1
        playerData[playerIndex]["train_points"] = int(playerData[playerIndex]["train_points"]) + 2
        sendPacketToPlayer(genExpMessage(playerID,int(playerData[playerIndex]["exp"])),playerID)
        sendPacketToPlayer(reloadCharacterPacket(playerIndex),playerID)
        packetToSend = genMessage(str(playerData[playerIndex]["name"]) + " has gained a level!",0,'#a0522d')
        sendToEveryoneOnline(packetToSend)

def handlePlayerEvents(playerIndex):
    global playerData
    if playerData[playerIndex].has_key("level") == True:
        level = int(playerData[playerIndex]["level"])
        exp = int(playerData[playerIndex]["exp"])
        expRequired = expRequiredForLevel(level)
        if exp >= expRequired:
            handleLevelUp(playerIndex)
    if int(playerData[playerIndex]["pos"]["map_id"]) < 0:
        leaveMap(playerIDList[playerIndex],int(0 - int(playerData[playerIndex]["pos"]["map_id"])))
    if playerData[playerIndex]["data"].has_key("dead") == False and playerData[playerIndex]["vitals"]["hp"] <= 0:
        playerData[playerIndex]["data"]["dead"] = int(time.time())
        sendPacketToPlayer(genMessage('You have died! You can press the pickup button (e) to revive in 2 seconds, otherwise you can wait for someone to revive you.',0,'#ff0000') ,int(playerIDList[playerIndex]))
        sendToAllOnMap(genPlaySound(3))
    elif playerData[playerIndex]["data"].has_key("dead") == True and playerData[playerIndex]["vitals"]["hp"] > 0:
        del playerData[playerIndex]["data"]["dead"]

def handleMapTile(x,y):
    global mapMeta
    global mapData
    global mapNPCs
    curTime = int(time.time())
    #print "checking tile " + str(x) + "," + str(y)
    if mapData["tiles"][x][y]["type"] == 6:
        #print "checking if spawn needed.."
        #Is this npc handled?
        spawnNeeded = 1
        for i in range(len(mapMeta["mobs"])):
            if mapMeta["mobs"][i].has_key('tileSpawned') and mapMeta["mobs"][i]['tileSpawned'] == str(str(x) + ":" + str(y)):
                print "no spawn required"
                #we're good, they're spawned and covered
                spawnNeeded = 0
                break
        if spawnNeeded == 1 and mapData["tiles"][x][y]["data"].has_key('npc_id'):
            print "spawning npc....."
            npcID = mapData["tiles"][x][y]["data"]["npc_id"]
            d = mapData["tiles"][x][y]["data"]["dir"]
            spawnSlot = spawnNPC(npcID,x,y,d)
            if spawnSlot > -1:
                mapMeta["mobs"][spawnSlot]["tileSpawned"] = str(str(x) + ":" + str(y))
    elif mapData["tiles"][x][y]["type"] == 4:
        #spawnNeeded = 1
        tileStr = str(str(x) + ":" + str(y))
        if mapMeta.has_key("spawnItems") == False:
            mapMeta["spawnItems"] = {}
        if mapMeta["spawnItems"].has_key(tileStr) == False:
            mapMeta["spawnItems"][tileStr] = {}
            mapMeta["spawnItems"][tileStr]["mapItemSlot"] = -1
            mapMeta["spawnItems"][tileStr]["itemRespawn"] = 0
        if mapMeta["spawnItems"][tileStr]["mapItemSlot"] == -1 and int(mapMeta["spawnItems"][tileStr]["itemRespawn"] + 10) < int(curTime):
           print "itemRespawn:" + str(mapMeta["spawnItems"][tileStr]["itemRespawn"])
           itemID = mapData["tiles"][x][y]["data"]["item_id"]
           amount = mapData["tiles"][x][y]["data"]["amount"]
           if amount == 0:
               amount = 1
           if itemID > -1:
               mapItem = deepcopy(mapItemTemplate)
               mapItem["item_id"] = itemID
               mapItem["uses"] = itemDB[itemID]["uses"]
               mapItem["amount"] = int(amount)
               mapItem["x"] = int(x)
               mapItem["y"] = int(y)
               itemResult=addMapItem(mapItem)
               if itemResult != None:
                   slotID = int(json.loads(itemResult)["slot_id"])
                   mapMeta["spawnItems"][tileStr]["mapItemSlot"] = slotID
                   sendToAllOnMap(itemResult)
                   #addMapItem

def spawnNPC(npcID,x,y,d = -1):
    global mapNPCs
    global mapData
    curTick = int(time.time() * 1000)
    for i in range(len(mapData["spawn_npc_ids"])):
        if mapData["spawn_npc_ids"][i] == -1:
            if mapNPCs[i]["npc_id"] == -1:               
                mapMeta["mobs"][i]["aggroList"] = {}
                mapMeta["mobs"][i]["nextTick"] = curTick + 600
                npc_id = int(mapData["spawn_npc_ids"][i])
                mapNPCs[i]["npc_id"] = npcID
                mapNPCs[i]["sprite"] = mobDB[npcID]["sprite"]
                mapNPCs[i]["scale"] = mobDB[npcID]["scale"]
                mapNPCs[i]["vitals"] = deepcopy(mobDB[npcID]["vitals"])
                mobPos = {}
                mobPos["x"] = x
                mobPos["y"] = y
                if d == -1:
                    mobPos["dir"] = int(random.randint(0,3))
                else:
                    mobPos["dir"] = int(d)
                mobPos["map_id"] = mapID
                mapNPCs[i]["pos"] = mobPos
                sendToAllOnMap(genNPCUpdate(mapNPCs[i],i))
                return i
    return -1

def handleEvents():
    global mapMeta
    global mapNPCs
    global mapData
    curTime = int(time.time())
    #mob cleanup duty for anyone that died
    for i in range(len(mapNPCs)):
        if int(mapNPCs[i]["vitals"]["hp"]) <= 0 and int(mapNPCs[i]["npc_id"]) > -1:
            handleNPCDeath(i)
    for x in range(len(mapData["tiles"])):
        for y in range(len(mapData["tiles"][x])):
            handleMapTile(x,y)
    for i in range(len(playerData)):
        handlePlayerEvents(i)

    if mapMeta.has_key("doors") == False or len(mapMeta["doors"]) < 20:
        mapMeta["doors"] = []
        for i in range(len(mapDoors)):
            mapMeta["doors"].append(-1)

    doorsClosed = 0
    for i in range(len(mapDoors)):
        if mapMeta["doors"][i] > -1 and int(mapMeta["doors"][i]) <= curTime:
            mapMeta["doors"][i] = -1
            mapDoors[i]["x"] = -1
            mapDoors[i]["y"] = -1
            doorsClosed = 1
    if doorsClosed == 1:
        sendToAllOnMap(genMapDoors())



def openDoor(xPos,yPos,duration = 10,refreshTimer = False):
    needDoor = -1
    for i in range(len(mapDoors)):
        if needDoor == -1 and mapMeta["doors"][i] == -1:
            needDoor = i
        if mapDoors[i]["x"] == xPos and mapDoors[i]["y"] == yPos:
            if refreshTimer == True:
                mapMeta["doors"][i] = (int(time.time()) + 10)
            return False
    if needDoor > -1:
        mapDoors[needDoor]["x"] = xPos
        mapDoors[needDoor]["y"] = yPos
        mapMeta["doors"][needDoor] = int(int(time.time()) + 10)
        return True

def checkDoorOpen(xPos,yPos):
    for i in range(len(mapDoors)):
        if mapDoors[i]["x"] == xPos and mapDoors[i]["y"] == yPos:
            return True
    return False

def genMapDoors():
    global mapDoors
    global mapID
    packet = {}
    packet["type"] = 122
    packet["map_id"] = mapID
    packet["map_doors"] = mapDoors
    return json.dumps(packet)

def reloadCharacterPacket(playerIndex = None,playerID = None):
    if playerIndex == None and playerID == None:
        return
    elif playerIndex == None:
        playerIndex = int(playerIDToIndex(playerID))
    elif playerID == None:
        playerID = int(playerIDList[playerIndex])
    packet = {}
    packet["type"] = 109
    packet["player_id"] = playerID
    packet["player"] = deepcopy(playerData[playerIndex])
    #we're not giving away player data, the client doesn't NEED it
    packet["player"]["data"] = []
    return json.dumps(packet)

def handleTick():
    global mapMeta
    nextTick = -1
    lowestTick = -1
    #Check all mobs
    curTick = int(time.time() * 1000)
    curTime = int(time.time())
    if mobDB == None:
        loadMobDB()
    if mapMeta != None:
        print ("curTick:" + str(curTick))
        #print mapMeta
        for i in range(len(mapNPCs)):
            #print ("mapNPCs[" + str(i) + "][\"npc_id\"] =" + str(int(mapNPCs[i]["npc_id"])) + " nextTick:" + str(int(mapMeta["mobs"][int(i)]["nextTick"])))
            #We're giving ourselves a 25 millisecond buffer
            nextTick = int(mapMeta["mobs"][i]["nextTick"])
            if int(mapNPCs[i]["npc_id"]) > -1 and mapNPCs[i]["vitals"]["hp"] > 0 and int(mapMeta["mobs"][i]["nextTick"]) <= int(curTick + graceBuffer):
                nextTick = int(mapMeta["mobs"][i]["nextTick"])
                topAggro = 0
                aggroPlayer = -1
                tmpAggroPlayer = -1
                aggroPath = None
                #mapNPCs[i]["pos"]["x"] = 7
                #mapNPCs[i]["pos"]["y"] = 4
                mob_x = int(mapNPCs[i]["pos"]["x"])
                mob_y = int(mapNPCs[i]["pos"]["y"])
                if len(mapMeta["mobs"][i]["aggroList"]) > 0:
                    for pID in mapMeta["mobs"][i]["aggroList"]:
                        if int(mapMeta["mobs"][i]["aggroList"][str(pID)]) > topAggro:
                            playerIndex = playerIDToIndex(int(pID))
                            if playerIndex > -1 and playerData[playerIndex]["vitals"]["hp"] > 0 and playerData[playerIndex]["sprite"] > -1:
                                player_x = int(playerData[playerIndex]["pos"]["x"])
                                player_y = int(playerData[playerIndex]["pos"]["y"])
                                result = mobAStar(mapData["tiles"],(mob_x,mob_y),(player_x,player_y))
                                tmpAggroPlayer = int(pID)
                                if result != 'NF':
                                    topAggro = int(mapMeta["mobs"][i]["aggroList"][str(pID)])
                                    aggroPlayer = int(pID)
                                    aggroPath = result

                #if we couldn't path to anyone, set the primary aggro target to the person with the highest aggro
                if aggroPlayer == -1:
                    aggroPlayer = tmpAggroPlayer
                scriptOverride = 0
                try:
                    prepScript('mobai')
                    import script_mobai
                    reload(script_mobai)

                    if aggroPath == None:
                        travelLen = -1
                    else:
                        travelLen = len(aggroPath)
                    if str("mobaiTick_" + str(mapNPCs[i]["npc_id"])) in dir(script_mobai):
                        sendVariablesToScript()
                        scriptOverride = getattr(script_mobai,'mobaiTick_' + str(str(mapNPCs[i]["npc_id"])))(i,aggroPlayer,int(travelLen))
                        loadVariablesFromScript()
                    elif "genericaiTick" in dir(script_mobai):
                        sendVariablesToScript()
                        
                        scriptOverride = getattr(script_mobai,'genericaiTick')(i,aggroPlayer,int(travelLen))
                        loadVariablesFromScript()
                    loadScriptPackets()
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                    print "mobaiTick Failed!"
                    pass
                if mapMeta["mobs"][i].has_key('speed_modifier'):
                    speedModifier = int(mapMeta["mobs"][i]['speed_modifier'])
                else:
                    speedModifier = 0
                if aggroPlayer > -1 and aggroPath != None and scriptOverride == 0:
                    if len(aggroPath[1:]) == 1:
                        mobSpeed = 0
                    
                    nextTick = int(mapMeta["mobs"][i]["nextTick"])
                    if nextTick == 0:
                        nextTick = curTick
                    pursue_run = 0
                    moveAmount = mobDB[int(mapNPCs[i]["npc_id"])]["move_amount"]
                    if moveAmount < 1:
                        moveAmount = 1
                    movement_delay = float(float(mobDB[int(mapNPCs[i]["npc_id"])]["move_delay"]) / 100.0)
                    if mobDB[int(mapNPCs[i]["npc_id"])]["pursue_run"] == True:
                        pursue_run = 1
                    mobSpeed = (((600 - (300 * pursue_run)) * movement_delay) / moveAmount) + speedModifier
                    if mobSpeed <= 100:
                        mobSpeed = 100
                    if len(aggroPath[1:]) == 1:
                        d = checkDirFace(mob_x,mob_y,aggroPath[1][0],aggroPath[1][1],mapNPCs[i]["pos"]["dir"])
                        if d != -1:
                            sendToAllOnMap(moveNPCTo(i,aggroPath[1][0],aggroPath[1][1],0))

                        scriptOverride = 0
                        try:
#                        if 1 == 1:
                            import script_mobai
                            if str("mobaiAttack_" + str(mapNPCs[i]["npc_id"])) in dir(script_mobai):
                                sendVariablesToScript()
                                getattr(script_mobai,'mobaiAttack_' + str(str(mapNPCs[i]["npc_id"])))(i,aggroPlayer)
                                loadVariablesFromScript()
                            elif "genericaiAttack" in dir(script_mobai):
                                sendVariablesToScript()
                                getattr(script_mobai,'genericaiAttack')(i,aggroPlayer)
                                loadVariablesFromScript()
                            loadScriptPackets()
                        except:
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                            print "mobaiTick Failed!"
                            pass

                        if (curTick - nextTick) > 1000:
                            nextTick = curTick
                        else:
                            nextTick += (1000 + speedModifier)
                    else:
                        sendToAllOnMap(moveNPCTo(i,aggroPath[1][0],aggroPath[1][1],mobSpeed))
                        if (curTick - nextTick) > 1000:
                            nextTick = (curTick - 1000) + mobSpeed #((600 - (300 * pursue_run)) * movement_delay
                        else:
                            nextTick += mobSpeed #((600 - (300 * pursue_run)) * movement_delay)                    
                elif scriptOverride == 0:
                    #print("passive movement..")
                    moveChance = mobDB[int(mapNPCs[i]["npc_id"])]["move_chance"]
                    moveAmount = mobDB[int(mapNPCs[i]["npc_id"])]["move_amount"]
                    movement_delay = float(float(mobDB[int(mapNPCs[i]["npc_id"])]["move_delay"]) / 100.0)
                    if moveAmount > 0:
                        mobSpeed = ((600 * movement_delay) / moveAmount) + speedModifier
                    else:
                        mobSpeed = ((600 * movement_delay) / 1) + speedModifier
                    if mobSpeed <= 200:
                        mobSpeed = 200
                    if (curTick - nextTick) > 1000:
                        nextTick = (curTick - 1000) + mobSpeed #* skipAmount
                    else:
                        nextTick += mobSpeed
                    #print("moving..." + str(moveAmount) + " times...")
                    moveAmount = 1
                    if int(random.randint(1,100)) <= moveChance:
                        for moves in range(moveAmount):
                            start_x = mob_x
                            start_y = mob_y
                            d = int(random.randint(0,3))
                            for attempts in range(3):
                                tmp_x = mob_x
                                tmp_y = mob_y
                                if d == 0 and mob_y < 11:
                                    tmp_y += 1
                                elif d == 1 and mob_x > 0:
                                    tmp_x -= 1
                                elif d == 2 and mob_x < 11:
                                    tmp_x += 1
                                elif d == 3 and mob_y > 0:
                                    tmp_y -= 1
                                pTileType = mapData["tiles"][tmp_x][tmp_y]["type"]
                                pTileData = mapData["tiles"][tmp_x][tmp_y]["data"]
                                if validMobSquare(pTileType,pTileData) == True and tileFree(tmp_x,tmp_y) == True:
                                    mob_x = tmp_x
                                    mob_y = tmp_y
                                    break
                                else:
                                    d = (d + 1) % 4
                            
                            if start_x != mob_x or start_y != mob_y:
                                #print("sending update...")
                                sendToAllOnMap(moveNPCTo(i,mob_x,mob_y,int(mobSpeed)))
                if scriptOverride == 0:
                    mapMeta["mobs"][i]["nextTick"] = nextTick
                else:
                    nextTick = curTick + 100#mapMeta["mobs"][i]["nextTick"]
                    mapMeta["mobs"][i]["nextTick"] = nextTick
                if lowestTick == -1 or lowestTick > nextTick:
                    lowestTick = nextTick
            elif int(mapNPCs[i]["npc_id"]) == -1 and mapNPCs[i]["vitals"]["hp"] <= 0:
#                print "npc index " + str(i) + " has an npc_id = -1... spawn_npc_id of " + str(int(mapData["spawn_npc_ids"][i])) + " respawn time of:" + str(int(mapMeta["mobs"][i]["respawnTime"]))
                if len(mapData["spawn_npc_ids"]) > i and int(mapData["spawn_npc_ids"][i]) > -1 and int(mapMeta["mobs"][i]["respawnTime"]) <= int(curTick + graceBuffer):
                    #we're going to try to find a spawn location 30 times; if we fail we'll give up
                    valid_x = -1
                    valid_y = -1
                    attempts = 0
                    while attempts < 30:
                        x = (random.randint(0,11))
                        y = (random.randint(0,11))
                        print ("attempting to spawn..(" + str(x) + "," + str(y) + ")")
                        pTileType = mapData["tiles"][x][y]["type"]
                        pTileData = mapData["tiles"][x][y]["data"]
                        if validMobSquare(pTileType,pTileData) == True:
                            valid_x = x
                            valid_y = y
                            break
                        attempts += 1
                    if valid_x > -1 and valid_y > -1:
                        mapMeta["mobs"][i]["speed_modifier"] = 0
                        mapMeta["mobs"][i]["aggroList"] = {}
                        mapMeta["mobs"][i]["nextTick"] = curTick + 600
                        npc_id = int(mapData["spawn_npc_ids"][i])
                        mapNPCs[i]["npc_id"] = npc_id
                        mapNPCs[i]["sprite"] = mobDB[npc_id]["sprite"]
                        mapNPCs[i]["scale"] = mobDB[npc_id]["scale"]
                        mapNPCs[i]["vitals"] = deepcopy(mobDB[npc_id]["vitals"])
                        mobPos = {}
                        mobPos["x"] = valid_x
                        mobPos["y"] = valid_y
                        mobPos["dir"] = int(random.randint(0,3))
                        mobPos["map_id"] = mapID
                        mapNPCs[i]["pos"] = mobPos
                        sendToAllOnMap(genNPCUpdate(mapNPCs[i],i))
                        sendToAllOnMap(moveNPCTo(i,valid_x,valid_y,0))
                        if lowestTick == -1:
                            nextTick = curTick + 600

            if nextTick > -1 and (lowestTick == -1 or lowestTick > nextTick) and int(mapNPCs[i]["npc_id"]) > -1:
                if nextTick < (curTick + 100):
                    nextTick = curTick + 100
                lowestTick = nextTick
    for i in range(len(playerIDList)):
        if playerData[i]["data"].has_key("nextTick") and int(playerData[i]["data"]["nextTick"]) <= curTick:
            scriptOverride = 0
            try:
                prepScript('playertick')
                import script_playertick
                reload(script_playertick)
                if "playertick" in dir(script_playertick):
                    sendVariablesToScript()
                    scriptOverride = getattr(script_playertick,'playertick')(playerIDList[i])
                    print "script override from playertick:" + str(scriptOverride)
                    loadVariablesFromScript()
                loadScriptPackets()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                print 'playertick script failed'
                pass

            pNextTick = int(playerData[i]["data"]["nextTick"])
            
            if pNextTick < (curTick + 100):
                print "pNextTick was " + str(pNextTick) + " defaulting to curTick + 100"
                pNextTick = curTick + 100
            if lowestTick == -1 or lowestTick > pNextTick:
                print "lowestTick came from player " + str(i) + " (" + str(pNextTick) + ")"
                lowestTick = pNextTick
        elif playerData[i]["data"].has_key("nextTick"): 
            pNextTick = int(playerData[i]["data"]["nextTick"])
            if lowestTick > pNextTick or lowestTick == -1:
                lowestTick = pNextTick
    if mapMeta.has_key("shots") == False:
        mapMeta["shots"] = []
        for i in range(50):
            mapMeta["shots"].append(deepcopy(mapMetaShotTemplate))
    else:
        for i in range(len(mapMeta["shots"])):
            if mapShots[i]["shooter_type"] > 0 and mapMeta["shots"][i]["nextTick"] < curTick:
                print "moving shot.."
                movesLeft = mapMeta["shots"][i]["movesLeft"]
                curX = mapMeta["shots"][i]["x"]
                curY = mapMeta["shots"][i]["y"]
                d = mapShots[i]["pos"]["dir"]
                shooterType = mapShots[i]["shooter_type"]
                shooterID = mapShots[i]["shooter_id"]
                shotItem = mapShots[i]["item_id"]
                shotX,shotY = [(curX,curY+1),(curX-1,curY),(curX+1,curY),(curX,curY-1)][d]
                movesLeft -= 1
                if shotX > -1 and shotX < 12 and shotY > -1 and shotY < 12 and movesLeft > 0:
                    print "shot still on map; checking for hit"
                    if projectileHitCheck(shooterType,shooterID,shotX,shotY,shotItem,d) == False:
                        print "not hit, moving forward"
                        mapMeta["shots"][i]["x"] = shotX
                        mapMeta["shots"][i]["y"] = shotY
                        mapMeta["shots"][i]["movesLeft"] = movesLeft
                        moveProjectile(i,shotX,shotY,d,150)
                        nextTick = curTick + 150
                        mapMeta["shots"][i]["nextTick"] = nextTick
                        if lowestTick > nextTick or lowestTick == -1:
                            lowestTick = nextTick
                        continue
                if shotX > -1 and shotX < 12 and shotY > -1 and shotY < 12 and movesLeft == 0:
                    projectileHitCheck(shooterType,shooterID,shotX,shotY,shotItem,d)
                #despawn and cleanup
                print "cleaning up shot..."
                mapMeta["shots"][i]["x"] = 0
                mapMeta["shots"][i]["y"] = 0
                mapMeta["shots"][i]["movesLeft"] = 0
                mapShots[i]["shooter_type"] = 0
                mapShots[i]["shooter_id"] = -1
                mapShots[i]["item_id"] = -1
                mapShots[i]["pos"]["x"] = 0
                mapShots[i]["pos"]["y"] = 0
                mapShots[i]["pos"]["dir"] = 0
                genMapShot(i,mapShots[i])
            elif mapShots[i]["shooter_type"] > 0:
                if (lowestTick > int(mapMeta["shots"][i]["nextTick"]) and int(mapMeta["shots"][i]["nextTick"]) > 0) or lowestTick == -1:
                    lowestTick = int(mapMeta["shots"][i]["nextTick"])
    #don't bug me for at least another 100 milliseconds!
#    if lowestTick > -1 and lowestTick < (curTick + 50):
#        lowestTick = (curTick + 50)
    print "lowest tick:" + str(lowestTick)
    return int(lowestTick)
#    if mapNPCs != None:
#        for i in len(mapNPCs):
#            if mapNPCs[""]

def genMapShot(mapSlot,mapShot):
    global mapShots
    packet = {}
    packet["type"] = 126
    packet["map_id"] = mapID
    packet["slot_id"] = mapSlot
    packet["map_shots"] = mapShot
    sendToAllOnMap(json.dumps(packet))

def sendAllMapShots():
    global mapShots
    packet = {}
    packet["type"] = 126
    packet["map_id"] = mapID
    packet["map_shots"] = mapShots
    return json.dumps(packet)

def moveProjectile(slotID,x,y,d,speed = 150):
    packet = {}
    packet["type"] = 127
    packet["map_id"] = mapID
    packet["slot_id"] = slotID
    packet["x"] = x
    packet["y"] = y
    packet["dir"] = d
    packet["speed"] = speed
    sendToAllOnMap(json.dumps(packet))

def projectileHitCheck(shooterType,shooterID,shotX,shotY,shotItem,direction):
    if mapData["tiles"][shotX][shotY]["type"] == 1 and mapData["tiles"][shotX][shotY]["data"].has_key('block_ranged') and mapData["tiles"][shotX][shotY]["data"]["block_ranged"] == True:
        return True
    for i in range(len(playerIDList)):
        if playerData[i]["pos"]["x"] == shotX and playerData[i]["pos"]["y"] == shotY:
            scriptOverride = 0
            try:
                prepScript('projectile')
                import script_projectile
                reload(script_projectile)
                if "hitplayer" in dir(script_projectile):
                    sendVariablesToScript()
                    scriptOverride = getattr(script_projectile,'hitplayer')(playerData[i],shooterType,shooterID,shotX,shotY,shotItem,direction)
                    loadVariablesFromScript()
                elif "hitgeneric" in dir(script_projectile):
                    sendVariablesToScript()
                    scriptOverride = getattr(script_projectile,'hitgeneric')(1,playerData[i],shooterType,shooterID,shotX,shotY,shotItem,direction)
                    loadVariablesFromScript()
                loadScriptPackets()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                print 'projectile player Hit script failed'
            if scriptOverride == 1:
                return True
    for i in range(len(mapNPCs)):
        if mapNPCs[i]["npc_id"] > -1 and mapNPCs[i]["vitals"]["hp"] > 0 and mapNPCs[i]["pos"]["x"] == shotX and mapNPCs[i]["pos"]["y"] == shotY:
            scriptOverride = 0
            try:
                prepScript('projectile')
                import script_projectile
                reload(script_projectile)
                if "hitnpc" in dir(script_projectile):
                    sendVariablesToScript()
                    scriptOverride = getattr(script_projectile,'hitnpc')(i,shooterType,shooterID,shotX,shotY,shotItem,direction)
                    loadVariablesFromScript()
                elif "hitgeneric" in dir(script_projectile):
                    sendVariablesToScript()
                    scriptOverride = getattr(script_projectile,'hitgeneric')(2,i,shooterType,shooterID,shotX,shotY,shotItem,direction)
                    loadVariablesFromScript()
                loadScriptPackets()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                print 'projectile mob Hit script failed'
            if scriptOverride == 1:
                return True
    return False

SERVER_ID=str(uuid.uuid4())
while True:
    print "attempting to read from mapWQ"
    tmp=r.blpop('mapWQ', 0)[1]
    if tmp == None:
        continue
    if tmp != 'None' and int(tmp) > -1:
        startTime = int(time.time() * 1000)
        #Do we need to worry about this?
        if r.get('map' + str(tmp) + 'Handled') == None:
            #Okay, map attention is required; lets try to pick it up
            pl = r.pipeline()
            pl.set('map' + str(tmp) + 'Handled',SERVER_ID,None,15000,True)
            pl.get('map' + str(tmp) + 'Handled')
            result = pl.execute()
            if result[1] == SERVER_ID:
                print "handling map " + str(tmp)
                mapID = tmp
                mapData = None
                pl = r.pipeline()
                pl.lrange('map' + str(tmp) + 'Queue',0,-1)
                pl.lrange('map' + str(tmp) + 'Task',0,-1)
                pl.lrange('map' + str(tmp) + 'Players',0,-1)
                pl.lrange('map' + str(tmp) + 'NewPlayers',0,-1)
                pl.lrange('map' + str(tmp) + 'removePlayers',0,-1)
                pl.delete('map' + str(tmp) + 'Queue')
                pl.delete('map' + str(tmp) + 'Task')
                pl.delete('map' + str(tmp) + 'NewPlayers')
                pl.delete('map' + str(tmp) + 'removePlayers',0,-1)
                result = pl.execute()
#                if result[4] != None:
#                    PL = r.pipeline()
#                    for i in range(len(result[4])):
#                        print "leaving game..." + str(i)
#                        leaveMap(result[4][i],-1)
#                    PL.execute()
                if result[0] == None and result[1] == None and result[3] == None:
                    #Race condition or something got us here.. lets skip
                    continue
                playerIDList = result[2]
                newCharacterList = result[3]
                if newCharacterList != None:
                    for i in range(len(newCharacterList)):
                        playerIDList.append(int(newCharacterList[i]))
                pl = r.pipeline()
                pl.get('map' + str(tmp) + 'Data')
                pl.get('map' + str(tmp) + 'Npcs')
                pl.get('map' + str(tmp) + 'Doors')
                pl.get('map' + str(tmp) + 'Shots')
                pl.get('map' + str(tmp) + 'Items')
                pl.get('map' + str(tmp) + 'Meta')
                for i in range(len(playerIDList)):
                    pl.get('pD_' + str(playerIDList[i]))
                resourceFetch = pl.execute()
                if resourceFetch[0] != None:
                    mapData = json.loads(resourceFetch[0])
                else:
                    mapData = mapTemplate
                if resourceFetch[1] != None:
                    mapNPCs = json.loads(resourceFetch[1])
                else:
                    mapNPCs = deepcopy(mapNPCsTemplate)
                if resourceFetch[2] != None:
                    mapDoors = json.loads(resourceFetch[2])
                    if len(mapDoors) == 0:
                        mapDoors = deepcopy(mapDoorTemplate)
                else:
                    mapDoors = deepcopy(mapDoorTemplate)
                if resourceFetch[3] != None:
                    mapShots = json.loads(resourceFetch[3])
                else:
                    mapShots = deepcopy(mapShotsTemplate)
                if resourceFetch[4] != None:
                    mapItems = json.loads(resourceFetch[4])
                else:
                    mapItems = deepcopy(mapItemsTemplate)
                if resourceFetch[5] != None:
                    mapMeta = json.loads(resourceFetch[5])
                else:
                    mapMeta = deepcopy(mapMetaTemplate)
                playerData = []
                #I don't like this, rewrite with something better
                playerIDList_tmp= []
                for i in range(len(playerIDList)):
                    if resourceFetch[int(i+6)] != None:
                        playerData.append(json.loads(resourceFetch[int(i+6)]))
                        playerIDList_tmp.append(playerIDList[i])
                    else:
                        #Remove the player from the map since we have no player data
                        r.lrem('map' + str(mapID) + 'Players',0,str(playerIDList[i]))
                playerIDList = playerIDList_tmp

                if result[4] != None:
                    PL = r.pipeline()
                    for i in range(len(result[4])):
                        print "leaving game..." + str(i)
                        leaveMap(result[4][i],-1)
                    PL.execute()
                #lets take care of the new Players
                if newCharacterList != None:
                    PL = r.pipeline()
                    for i in range(len(newCharacterList)):
                        if mapMeta.has_key("players") == False:
                            mapMeta["players"] = {}
                        elif mapMeta["players"].has_key(str(newCharacterList[i])):
                            mapMeta["players"][str(newCharacterList[i])] = {}
                        scriptOverride = 0
                        try:
                            prepScript('joinmap')
                            import script_joinmap
                            reload(script_joinmap)
                            if "joinmap" in dir(script_joinmap):
                                sendVariablesToScript()
                                scriptOverride = getattr(script_joinmap,'joinmap')(newCharacterList[i])
                                loadVariablesFromScript()
                            loadScriptPackets()
                        except:
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                            print 'joinmap script failed'
                        if mapData.has_key("shop_id"):
                            shopID = int(mapData["shop_id"])
                        else:
                            shopID = -1
                        if shopID > -1:
                            loadShopDB()
                            shopName = str(shopDB[shopID]["name"])
                            shopJoin = str(shopDB[shopID]["join_say"])
                            if shopName != "" and shopJoin != "":
                                sendPacketToPlayer(genMessage(shopName + " says, '" + shopJoin + "'",1,'#d3d3d3'),int(newCharacterList[i]))

                        PL.rpush('map' + str(mapID) + 'Players',newCharacterList[i])
                        sendPacketToPlayer('{"type":106,"map_id":' + str(mapID) + ',"map":' + json.dumps(mapData) + '}',int(newCharacterList[i]))
                        sendPacketToPlayer('{"type":112,"map_id":' + str(mapID) + ',"map_items":' + json.dumps(mapItems) + '}',int(newCharacterList[i]))
                        newChar = spawnCharacter(int(len(playerIDList) - (1 + i)),newCharacterList[i])
                        sendPacketToPlayer(genMapDoors(),int(newCharacterList[i]))
                        sendPacketToPlayer(sendAllMapShots(),int(newCharacterList[i]))
                        sendPacketToPlayer(genAllNPCUpdate(),int(newCharacterList[i]))
                        if mapData["music_id"] > -1:
                            sendPacketToPlayer('{"type":124,"music_id":' + str(mapData["music_id"]) + '}',newCharacterList[i])
                        for x in range(len(playerIDList)):
                            existingChar = spawnCharacter(x,playerIDList[x])
                            movePacket = {}
                            movePacket["type"] = 115
                            movePacket["player_id"] = int(playerIDList[x])
                            movePacket["x"] = playerData[x]["pos"]["x"]
                            movePacket["y"] = playerData[x]["pos"]["y"]
                            movePacket["dir"] = playerData[x]["pos"]["dir"]
                            movePacket["speed"] = 0
                            sendPacketToPlayer(newChar,int(playerIDList[x]))
                            sendPacketToPlayer(existingChar,int(newCharacterList[i]))
                            sendPacketToPlayer(json.dumps(movePacket),int(newCharacterList[i]))
                    PL.execute()
                PL = r.pipeline()
                nextTick = int(handleTick())
                if nextTick > -1 and len(playerIDList) > 0:
                    PL.rpush('pokeRequests', str(mapID) + " " + str(nextTick))
                PL.execute()
                
                while len(result[0]) > 0 or len(result[1]) > 0:
                    PL = r.pipeline()
                    if len(result[0]) > 0:
                        print("Processing map " + str(tmp) + " packet queue..." )
                        for i in range(len(result[0])):
                            print("Processing map " + str(tmp) + " packet queue..." )
                            rawPacket=str(result[0][i].decode('utf8'))
                            processPacket(rawPacket)
                    if len(result[1]) > 0:
                        print("Processing map " + str(tmp) + " task queue..." )
#                        for i in range(len(result[1])):
#                            print("Processing map " + str(tmp) + " task queue..." )
                            #processTask(result[0][i])
                    handleEvents()
                    PL.execute()
                    pl = r.pipeline()
                    pl.lrange('map' + str(tmp) + 'Queue',0,-1)
                    pl.lrange('map' + str(tmp) + 'Task',0,-1)
                    pl.delete('map' + str(tmp) + 'Queue')
                    pl.delete('map' + str(tmp) + 'Task')
                    result = pl.execute()
                pl = r.pipeline()
                pl.set('map' + str(tmp) + 'Data',json.dumps(mapData))
                pl.set('map' + str(tmp) + 'Npcs',json.dumps(mapNPCs))
                pl.set('map' + str(tmp) + 'Doors',json.dumps(mapDoors))
                pl.set('map' + str(tmp) + 'Shots',json.dumps(mapShots))
                pl.set('map' + str(tmp) + 'Items',json.dumps(mapItems))
                pl.set('map' + str(tmp) + 'Meta',json.dumps(mapMeta))
                pl.delete('map' + str(tmp) + 'Handled')
                #pl.set('players',playerIDList)
                for i in range(len(playerIDList)):
                    pl.set('pD_' + str(playerIDList[i]),json.dumps(playerData[i]))
                pl.execute()
        print("processing time:" + str(int(int(time.time()*1000)-startTime)))
    #print "Processing map..." + str(tmp)
    
