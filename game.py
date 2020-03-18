import json
import time
from copy import deepcopy

playerData = []
playerIDList = []
mapData = {}
mapNPCs = []
mapDoors = []
mapShots = []
mapID = -1
mapItems = []
mobDB = None
itemDB = None
mapMeta = {}
scriptPackets = {}
professionDB = None

def loadVariables(loadMe):
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
    global professionDB
    if loadMe.has_key('playerData') and loadMe.has_key('playerIDList') and loadMe.has_key('mapData') and loadMe.has_key('mapNPCs') and loadMe.has_key('mapDoors') and loadMe.has_key('mapShots') and loadMe.has_key('mapID') and loadMe.has_key('mapItems') and loadMe.has_key('mobDB') and loadMe.has_key('itemDB') and loadMe.has_key('mapMeta'):
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
        professionDB = loadMe["professionDB"]

        #print "loaded variables for scripting..."

def getVariables():
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
    loadMe["scriptPackets"] = scriptPackets
    scriptPackets = {}
    #print "returned variables..."
    return loadMe

def playerIDToIndex(playerID):
    global playerIDList
    for i in range(len(playerIDList)):
        if int(playerID) == int(playerIDList[i]):
            return i
    return -1

def getPlayerName(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["name"]
    return ''

def getPlayerLevel(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["level"]
    return 0

def getPlayerX(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["pos"]["x"]
    return -1

def getPlayerY(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["pos"]["y"]
    return -1

def getPlayerDir(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["pos"]["dir"]
    return -1

def getPlayerHP(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["vitals"]["hp"]
    return -1

def getPlayerID(playerName):
    for i in range(len(playerIDList)):
        if playerData[i]["name"].lower() == playerName.lower():
            return playerIDList[i]
    return -1

def getPlayerMP(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["vitals"]["mp"]
    return -1

def getPlayerSP(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["vitals"]["sp"]
    return -1

def getPlayerMaxHP(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["max_vitals"]["hp"] 
    return -1

def getPlayerMaxMP(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["max_vitals"]["mp"]
    return -1

def getPlayerMaxSP(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return playerData[playerIndex]["max_vitals"]["sp"]
    return -1

def getPlayerProfession(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return int(playerData[playerIndex]["profession_id"])
    return -1

def getProfessionStr(professionID):
    if professionID > -1 and professionID < len(professionDB):
        return professionDB[professionID]["stats"]["str"]
    return -1

def getProfessionDef(professionID):
    if professionID > -1 and professionID < len(professionDB):
        return professionDB[professionID]["stats"]["def"]
    return -1

def getProfessionMag(professionID):
    if professionID > -1 and professionID < len(professionDB):
        return professionDB[professionID]["stats"]["mag"]
    return -1

def getProfessionSpd(professionID):
    if professionID > -1 and professionID < len(professionDB):
        return professionDB[professionID]["stats"]["spd"]
    return -1

def getProfessionHP(professionID):
    if professionID > -1 and professionID < len(professionDB):
        return professionDB[professionID]["vitals"]["hp"]
    return -1

def getProfessionMP(professionID):
    if professionID > -1 and professionID < len(professionDB):
        return professionDB[professionID]["vitals"]["mp"]
    return -1

def getProfessionSP(professionID):
    if professionID > -1 and professionID < len(professionDB):
        return professionDB[professionID]["vitals"]["sp"]
    return -1


def getProfessionName(professionID):
    if professionID > -1 and professionID < len(professionDB):
        return professionDB[profID]["name"]

def getPlayerStr(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        profID = playerData[playerIndex]["profession_id"]
        playerStr = professionDB[profID]["stats"]["str"] + playerData[playerIndex]["stats"]["str"]
        return int(playerStr)
    return 0

def getPlayerDef(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        profID = playerData[playerIndex]["profession_id"]
        playerDef = professionDB[profID]["stats"]["def"] + playerData[playerIndex]["stats"]["def"]
        return int(playerDef)
    return 0


#def getPlayerMeleeProtection(playerID):


def getPlayerSpd(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        profID = playerData[playerIndex]["profession_id"]
        playerSpd = professionDB[profID]["stats"]["spd"] + playerData[playerIndex]["stats"]["spd"]
        return int(playerSpd)
    return 0

def getPlayerMag(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        profID = playerData[playerIndex]["profession_id"]
        playerMag = professionDB[profID]["stats"]["mag"] + playerData[playerIndex]["stats"]["mag"]
        return int(playerMag)
    return 0

def getPlayerTrainPoints(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return int(playerData[playerIndex]["train_points"])
    return 0

def setPlayerTrainPoints(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["train_points"] = int(amount)
        reloadCharacterPacket(playerID)

def setPlayerStr(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["str"] = int(amount)
        calculateMaxVitals(playerID)
        reloadCharacterPacket(playerID)
    return

def setPlayerDef(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["def"] = int(amount)
        calculateMaxVitals(playerID)
        reloadCharacterPacket(playerID)
    return

def setPlayerSpd(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["spd"] = int(amount)
        calculateMaxVitals(playerID)
        reloadCharacterPacket(playerID)
    return

def setPlayerMag(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["mag"] = int(amount)
        calculateMaxVitals(playerID)
        reloadCharacterPacket(playerID)
    return

def setPlayerMinPAtk(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["pamin"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMaxPAtk(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["pamax"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMinRAtk(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["ramin"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMaxRAtk(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["ramax"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMinMAtk(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["mamin"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMaxMAtk(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["mamax"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMinPDef(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["pdmin"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMaxPDef(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["pdmax"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMinRDef(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["rdmin"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMaxRDef(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["rdmax"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMinMDef(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["mdmin"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def setPlayerMaxMDef(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["stats"]["mdmax"] = int(amount)
        reloadCharacterPacket(playerID)
    return

def getPlayerMinPAtk(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("pamin"):
        return int(playerData[playerIndex]["stats"]["pamin"])
    return 0

def getPlayerMaxPAtk(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("pamax"):
        return int(playerData[playerIndex]["stats"]["pamax"])
    return 0

def getPlayerMinRAtk(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("ramin"):
        return int(playerData[playerIndex]["stats"]["ramin"])
    return 0

def getPlayerMaxRAtk(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("ramax"):
        return int(playerData[playerIndex]["stats"]["ramax"])
    return 0

def getPlayerMinMAtk(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("mamin"):
        return int(playerData[playerIndex]["stats"]["mamin"])
    return 0

def getPlayerMaxMAtk(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("mamax"):
        return int(playerData[playerIndex]["stats"]["mamax"])
    return 0

def getPlayerMinPDef(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("pdmin"):
        return int(playerData[playerIndex]["stats"]["pdmin"])
    return 0

def getPlayerMaxPDef(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("pdmax"):
        return int(playerData[playerIndex]["stats"]["pdmax"])
    return 0

def getPlayerMinRDef(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("rdmin"):
        return int(playerData[playerIndex]["stats"]["rdmin"])
    return 0

def getPlayerMaxRDef(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("rdmax"):
        return int(playerData[playerIndex]["stats"]["rdmax"])
    return 0

def getPlayerMinMDef(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("mdmin"):
        return int(playerData[playerIndex]["stats"]["mdmin"])
    return 0

def getPlayerMaxMDef(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and playerData[playerIndex]["stats"].has_key("mdmax"):
        return int(playerData[playerIndex]["stats"]["mdmax"])
    return 0


def getPlayerEXP(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        return int(playerData[playerIndex]["exp"])
    return -1

def addPlayerEXP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
         playerData[playerIndex]["exp"] += amount
         sendPacketToPlayer(genExpMessage(playerID,int(playerData[playerIndex]["exp"])),playerID)
    return -1

def getPlayerFlag(playerID,flagName):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
         if playerData[playerIndex]["data"].has_key(flagName):
             return playerData[playerIndex]["data"][str(flagName)]
    return None

def setPlayerFlag(playerID,flagName,flagValue):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
         playerData[playerIndex]["data"][str(flagName)] = flagValue
    return -1

def getPlayerAccess(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
         return playerData[playerIndex]["access"]
    return -1

def getPlayerSprite(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
         return playerData[playerIndex]["sprite"]
    return -1

def getPlayerNameColor(playerID):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
         return playerData[playerIndex]["color"]
    return -1


def setPlayerNameColor(playerID,color):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
         playerData[playerIndex]["color"] = color
         sendToAllOnMap(spawnCharacter(int(playerID)))
    return -1

def setPlayerSprite(playerID,sprite):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
         playerData[playerIndex]["sprite"] = sprite
         sendToAllOnMap(spawnCharacter(int(playerID)))
    return -1

def setPlayerHP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["vitals"]["hp"] = amount
        sendToAllOnMap(genPlayerVitalMessage(playerID))

def setPlayerMP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["vitals"]["mp"] = amount
        sendToAllOnMap(genPlayerVitalMessage(playerID))

def setPlayerSP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["vitals"]["sp"] = amount
        sendToAllOnMap(genPlayerVitalMessage(playerID))

def setPlayerMaxHP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        base=(playerData[playerIndex]["max_vitals"]["hp"])
        modifier=int(base - amount)
        playerData[playerIndex]["stats"]["maxhp"] = int(modifier)
        reloadCharacterPacket(playerID)
        sendToAllOnMap(genPlayerVitalMessage(playerID))

def setPlayerMaxMP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        base=(playerData[playerIndex]["max_vitals"]["mp"])
        modifier=int(base - amount)
        playerData[playerIndex]["stats"]["maxmp"] = int(modifier)
        reloadCharacterPacket(playerID)
        sendToAllOnMap(genPlayerVitalMessage(playerID))

def setPlayerMaxSP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        base=(playerData[playerIndex]["max_vitals"]["sp"])
        modifier=int(base - amount)
        playerData[playerIndex]["stats"]["maxsp"] = int(modifier)
        reloadCharacterPacket(playerID)
        sendToAllOnMap(genPlayerVitalMessage(playerID))

def reducePlayerHP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["vitals"]["hp"] -= amount
        if playerData[playerIndex]["vitals"]["hp"] < 0:
            playerData[playerIndex]["vitals"]["hp"] = 0
        sendToAllOnMap(genPlayerVitalMessage(playerID))

def reducePlayerMP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["vitals"]["mp"] -= amount
        if playerData[playerIndex]["vitals"]["mp"] < 0:
            playerData[playerIndex]["vitals"]["mp"] = 0
        sendToAllOnMap(genPlayerVitalMessage(playerID))

def reducePlayerSP(playerID,amount):
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        playerData[playerIndex]["vitals"]["sp"] -= amount
        if playerData[playerIndex]["vitals"]["sp"] < 0:
            playerData[playerIndex]["vitals"]["sp"] = 0
        sendToAllOnMap(genPlayerVitalMessage(playerID))


def warpCharacter(playerID,x,y,direction = -1,newMap = -1):
    global mapID
    global playerData
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1 and x > -1 and x < 12 and y > -1 and y < 12:
        if direction > -1 and direction < 4:
            playerData[playerIndex]["pos"]["dir"] = direction
        playerData[playerIndex]["pos"]["x"] = int(x)
        playerData[playerIndex]["pos"]["y"] = int(y)
        sendToAllOnMap(spawnCharacter(int(playerID)))
        if newMap > -1:
            playerData[playerIndex]["pos"]["map_id"] = -newMap

def getInventorySlotItemID(playerID,slotID):
    global playerData
    if slotID > -1 and slotID < 30:
        playerIndex = playerIDToIndex(playerID)
        if playerIndex > -1:
            return int(playerData[playerIndex]["inv"][slotID]["item_id"])
    return -1

def getInventorySlotAmount(playerID,slotID):
    global playerData
    if slotID > -1 and slotID < 30:
        playerIndex = playerIDToIndex(playerID)
        if playerIndex > -1:
            return int(playerData[playerIndex]["inv"][slotID]["amount"])
    return -1

def getInventorySlotUses(playerID,slotID):
    global playerData
    if slotID > -1 and slotID < 30:
        playerIndex = playerIDToIndex(playerID)
        if playerIndex > -1:
            return int(playerData[playerIndex]["inv"][slotID]["uses"])
    return -1

def setInventorySlotItemID(playerID,slotID,itemID):
    global playerData
    if slotID > -1 and slotID < 30:
        playerIndex = playerIDToIndex(playerID)
        if playerIndex > -1:
            playerData[playerIndex]["inv"][slotID]["item_id"] = itemID
            sendPacketToPlayer(genInventoryUpdate(playerID,slotID),playerID)
    return -1

def setInventorySlotAmount(playerID,slotID,amount):
    global playerData
    if slotID > -1 and slotID < 30:
        playerIndex = playerIDToIndex(playerID)
        if playerIndex > -1:
            playerData[playerIndex]["inv"][slotID]["amount"] = amount
            sendPacketToPlayer(genInventoryUpdate(playerID,slotID),playerID)
    return -1

def setInventorySlotUses(playerID,slotID,uses):
    global playerData
    if slotID > -1 and slotID < 30:
        playerIndex = playerIDToIndex(playerID)
        if playerIndex > -1:
            playerData[playerIndex]["inv"][slotID]["uses"] = uses
            sendPacketToPlayer(genInventoryUpdate(playerID,slotID),playerID)
    return -1

def getItemMinDamage(itemID):
    global itemDB
    if itemID > -1 and itemID < 500:
        if itemDB[itemID]["data"].has_key('min_damage'):
            return int(itemDB[itemID]["data"]["min_damage"])
    return 0

def getItemMaxDamage(itemID):
    global itemDB
    if itemID > -1 and itemID < 500:
        if itemDB[itemID]["data"].has_key('max_damage'):
            return int(itemDB[itemID]["data"]["max_damage"])
    return 0

def getItemMinDefense(itemID):
    global itemDB
    if itemID > -1 and itemID < 500:
        if itemDB[itemID]["data"].has_key('min_protection'):
            return int(itemDB[itemID]["data"]["min_protection"])
    return 0

def getItemMaxDefense(itemID):
    global itemDB
    if itemID > -1 and itemID < 500:
        if itemDB[itemID]["data"].has_key('max_protection'):
            return int(itemDB[itemID]["data"]["max_protection"])
    return 0


def addItemToInventory(playerID,itemID,amount,uses):
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        for i in range(len(playerData[playerIndex]["inv"])):
            if i > 5:
                if playerData[playerIndex]["inv"][i]["item_id"] == -1:
                    playerData[playerIndex]["inv"][i]["item_id"] = itemID
                    playerData[playerIndex]["inv"][i]["amount"] = amount
                    playerData[playerIndex]["inv"][i]["uses"] = uses
                    sendPacketToPlayer(genInventoryUpdate(playerID,i),playerID)
                    return i
    return -1

def addItemToGround(itemID,amount,uses,x,y):
    global mapItems
    if itemID >= -1 and itemID <= 500 and amount >= -1 and uses >= -1:
        for i in range(len(mapItems)):
            if int(mapItems[i]["item_id"]) == -1:
                mapItem = {}
                mapItem["item_id"] = itemID
                mapItem["amount"] = amount
                mapItem["uses"] = uses
                mapItem["x"] = x
                mapItem["y"] = y
                sendToAllOnMap(genMapItemUpdate(i,mapItem))
                return i
    return -1

def getNpcID(mobID):
    global mapNPCs
    if mobID > -1 and mobID < 20:
        return int(mapNPCs[mobID]["npc_id"])
    return -1

def getNpcName(mobID):
    global mapNPCs
    global mobDB 
    if mobID > -1 and mobID < 20:
        mobType = mapNPCs[mobID]["npc_id"]
        if mobType > -1:
            return mobDB[mobType]["name"]
    return ''

def getNpcX(mobID):
    global mapNPCs
    if mobID > -1 and mobID < 20:
        return int(mapNPCs[mobID]["pos"]["x"])
    return -1

def getNpcY(mobID):
    global mapNPCs
    if mobID > -1 and mobID < 20:
        return int(mapNPCs[mobID]["pos"]["y"])
    return -1

def getNpcDir(mobID):
    global mapNPCs
    if mobID > -1 and mobID < 20:
        print "NPC DIR:" + str(mapNPCs[mobID]["pos"]["dir"])
        return int(mapNPCs[mobID]["pos"]["dir"])
    return -1


def getNpcHP(mobID):
    global mapNPCs
    if mobID > -1 and mobID < 20:
        return int(mapNPCs[mobID]["vitals"]["hp"])
    return -1

def getNpcMP(mobID):
    global mapNPCs
    if mobID > -1 and mobID < 20:
        return int(mapNPCs[mobID]["vitals"]["mp"])
    return -1

def getNpcSP(mobID):
    global mapNPCs
    if mobID > -1 and mobID < 20:
        return int(mapNPCs[mobID]["vitals"]["sp"])
    return -1

def getNpcStr(mobID):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            return int(mobDB[mobType]["stats"]["str"])
    return -1

def getNpcDef(mobID):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            return int(mobDB[mobType]["stats"]["def"])
    return -1

def getNpcSpd(mobID):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            return int(mobDB[mobType]["stats"]["spd"])
    return -1

def getNpcMag(mobID):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            return int(mobDB[mobType]["stats"]["mag"])
    return -1

def getNpcMaxHP(mobID):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            return int(mobDB[mobType]["vitals"]["hp"])
    return -1

def getNpcMaxMP(mobID):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            return int(mobDB[mobType]["vitals"]["mp"])
    return -1

def getNpcMaxSP(mobID):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            return int(mobDB[mobType]["vitals"]["sp"])
    return -1

def setNpcHP(mobID,amount):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            mapNPCs[mobID]["vitals"]["hp"] = int(amount)
            sendToAllOnMap(genMobVitalMessage(mobID))

def setNpcMP(mobID,amount):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            mapNPCs[mobID]["vitals"]["mp"] = int(amount)
            sendToAllOnMap(genMobVitalMessage(mobID))

def setNpcSP(mobID,amount):
    global mapNPCs
    global mobDB
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            mapNPCs[mobID]["vitals"]["sp"] = int(amount)
            sendToAllOnMap(genMobVitalMessage(mobID))

def getNpcSpeedModifier(mobID):
    global mapMeta
    if mobID > -1 and mobID < 20:
        if mapMeta["mobs"][mobID].has_key('speed_modifier'):
            return int(mapMeta["mobs"][mobID]['speed_modifier'])
    return 0

def setNpcSpeedModifier(mobID,amount):
    global mapMeta
    if mobID > -1 and mobID < 20:
        mapMeta["mobs"][mobID]['speed_modifier'] = int(amount)


def getNpcFlag(mobID,flagName):
    global mapMeta
    if mobID > -1 and mobID < 20:
        if mapMeta["mobs"][mobID].has_key("data"):
            if mapMeta["mobs"][mobID]["data"].has_key(flagName):
                return mapMeta["mobs"][mobID]["data"][flagName]
    return None

def setNpcFlag(mobID,flagName,flagValue):
    global mapMeta
    if mobID > -1 and mobID < 20:
        if mapMeta["mobs"][mobID].has_key("data") == False:
            mapMeta["mobs"][mobID]["data"] = {}
        mapMeta["mobs"][mobID]["data"][flagName] = flagValue

def getMapFlag(flagName):
    global mapMeta
    if mapMeta.has_key("map") == True and mapMeta["map"].has_key("data") == True:
        return mapMeta["map"]["data"][flagName]
    return None

def setMapFlag(flagName,flagValue):
    global mapMeta
    if mapMeta.has_key("map") == False:
        mapMeta["map"] = {}
    if mapMeta["map"].has_key("data") == False:
        mapMeta["map"]["data"] = {}
    mapMeta["mobs"]["data"][flagName] = flagValue


def getPlayersInRange(x,y,rangeSize):
    global playerData
    global playerIDList
    result = []
    if rangeSize >= 0:
        print "Checking players in range:"
        for i in range(len(playerIDList)):
            #print "PlayerData[" + str(i) + "][x] = " + str(int(playerData[i]["x"])) + "   PlayerData[" + str(i) + "][y] = " + str(int(playerData[i]["y"]))
            #print "x: " + str(x) + "  y:" + str(y)
            if abs(int(playerData[i]["pos"]["x"]) - int(x)) <= int(rangeSize) and abs(int(playerData[i]["pos"]["y"]) - int(y)) <= int(rangeSize):
                print "adding player to inrange"
                result.append(playerIDList[i])
    return result

def getMobsInRange(x,y,rangeSize):
    global mapNPCs
    result = []
    if rangeSize >= 0:
        for i in range(len(mapNPCs)):
            if mapNPCs[i]["npc_id"] > -1:
                if abs(int(mapNPCs[i]["pos"]["x"]) - x) <= rangeSize and abs(int(mapNPCs[i]["pos"]["y"]) - y) <= rangeSize:
                    result.append(i)
    return result

def getAggroList(mobID,minAggro = 0):
    global mapMeta
    retList = []
    if mobID > -1 and mobID < 20:
        if mapMeta["mobs"][mobID].has_key('aggroList'):
            for playerID in mapMeta["mobs"][mobID]["aggroList"]:
                if int(mapMeta["mobs"][mobID]["aggroList"][playerID]) > 0:
                    retList.append( (int(playerID),int(mapMeta["mobs"][mobID]["aggroList"][playerID])))
    return retList

def getAggro(mobID,playerID):
    global mapMeta
    if mobID > -1 and mobID < 20:
        if mapMeta["mobs"][mobID]["aggroList"].has_key(str(playerID)):
            return mapMeta["mobs"][mobID]["aggroList"][str(playerID)]
    return 0

def setAggro(mobID,playerID,amount):
    global mapMeta
    if mobID > -1 and mobID < 20:
        if mapMeta["mobs"][mobID]["aggroList"].has_key(str(playerID)) and amount == 0:
            del mapMeta["mobs"][mobID]["aggroList"][str(playerID)]
        else:
            mapMeta["mobs"][mobID]["aggroList"][str(playerID)] = int(amount)

def addAggro(mobID,playerID,amount):
    global mapMeta
    if mobID > -1 and mobID < 20:
        if mapMeta["mobs"][mobID]["aggroList"].has_key(str(playerID)):
            mapMeta["mobs"][mobID]["aggroList"][str(playerID)] = int(mapMeta["mobs"][mobID]["aggroList"][str(playerID)]) + int(amount)
        else:
            mapMeta["mobs"][mobID]["aggroList"][str(playerID)] = int(amount)

def getNpcBehavior(mobID):
    if mobID > -1 and mobID < 20:
        mobType = mapNPCs[mobID]["npc_id"]
        if mobType > -1:
            return mobDB[mobType]["behavior"]
    return -1

def mobAttack(mobID,playerAttacked,damage):
    HP = getPlayerHP(playerAttacked)
    if HP <= 0:
        return
    if int(damage) > int(HP):
        setPlayerHP(playerAttacked,0)
    else:
        setPlayerHP(playerAttacked,int(HP - damage))
    sendToAllOnMap(genMobAttackAnimation(mobID))
    npcName = getNpcName(mobID)
    createPlayerMapMessage(playerAttacked,str(damage),'#ff0000')
    sendPacketToPlayer(genMessage("A " + str(npcName) + " hit you for " + str(damage) + " damage.",4,'#ff0000',True),playerAttacked)
    sendToAllOnMap(genPlaySound(1))

def mobMiss(mobID,playerAttacked):
    npcName = getNpcName(mobID)
    createPlayerMapMessage(playerAttacked,'MISS','#ff0000')
    sendPacketToPlayer(genMessage("A " + str(npcName) + " missed you!",4,'#ff0000',True),playerAttacked)
    sendToAllOnMap(genPlaySound(4))

def playerMiss(attackerID,playerAttacked):
    attackerName = getPlayerName(attackerID)
    createPlayerMapMessage(playerAttacked,'MISS','#ff0000')
    sendPacketToPlayer(genMessage("A " + str(attackerName) + " missed you!",4,'#ff0000',True),playerAttacked)
    sendToAllOnMap(genPlaySound(4))

def healPlayer(playerID,targetID,amount,displayMsg = '',addsAggro = True):
    curHP = int(getPlayerHP(targetID))
    maxHP = int(getPlayerMaxHP(targetID))
    if curHP > 0:
        if displayMsg == '':
            displayMsg = str(amount)
        
        createPlayerMapMessage(targetID,str(displayMsg),'#00ff00')
        curHP += int(amount)
        if curHP > maxHP:
            curHP = maxHP
        setPlayerHP(targetID,curHP)
        if addsAggro == True:
            for i in range(len(mapNPCs)):
                if int(mapNPCs[i]["npc_id"]) > -1 and mapNPCs[i]["vitals"]["hp"] > 0 and mapMeta["mobs"][i]["aggroList"].has_key(str(targetID)):
                    addAggro(i,playerID, int(1+float(amount)*0.75))

def playerAttack(playerID,PcOrMob,attackedID,damage,addsAggro = True,attackAnimation = True):
    #hitting mob
    #print "attacking mob"
    curHP = getPlayerHP(playerID)
    if curHP > 0:
        if PcOrMob == 2 and mapData["protect_npcs"] == False:
            HP = getNpcHP(attackedID)
            if HP <= 0:
                return
            flavourText = ''
            if getNpcDir(attackedID) == getPlayerDir(playerID):
                damage = int(damage * 1.15)
                flavourText = ' from behind'
            if int(damage) > int(HP):
                setNpcHP(attackedID,0)
            else:
                setNpcHP(attackedID,int(HP - damage))
            npcName = getNpcName(attackedID)
            if addsAggro == True:
                addAggro(attackedID,playerID,damage)
            createNPCMapMessage(attackedID,str(damage),'#ff0000')
            sendPacketToPlayer(genMessage("You hit a " + str(npcName) + flavourText + " for " + str(damage) + " damage.",4,'#ffffff',True),playerID)
        elif PcOrMob == 1 and int(mapData["moral"]) < 2:
            print "attacking player"
            HP = getPlayerHP(attackedID)
            if HP <= 0:
                return
            flavourText = ''
            if getPlayerDir(attackedID) == getPlayerDir(playerID):
                damage = int(damage * 1.15)
                flavourText = ' from behind'
            if int(damage) > int(HP):
                setPlayerHP(attackedID,0)
            else:
                setPlayerHP(attackedID,int(HP - damage))
            attackedName = getPlayerName(attackedID)
            attackerName = getPlayerName(playerID)
            createPlayerMapMessage(attackedID,str(damage),'#ff0000')
            sendPacketToPlayer(genMessage("You hit " + str(attackedName) + flavourText + " for " + str(damage) + " damage.",4,'#ffffff',True),playerID)
            sendPacketToPlayer(genMessage(str(attackerName) + " hit you" + str(flavourText) + " for " + str(damage) + " damage.",4,'#ff0000',True),attackedID)
        else:
            sendPacketToPlayer(genMessage("You have nothing to attack.",4,'#ffffff',True),playerID)
            return
        print "sending attack Animation"
        if attackAnimation == True:
            sendToAllOnMap(genPlaySound(1))
            sendToAllOnMap(genAttackAnimation(playerID))

def playerSpellAttack(playerID,PcOrMob,attackedID,damage,spellName = '',color = '#00ffff',addsAggro = True,attackAnimation = True):
    #hitting mob
    #print "attacking mob"
    curHP = getPlayerHP(playerID)
    if PcOrMob == 2 and mapData["protect_npcs"] == False:
        HP = getNpcHP(attackedID)
        if HP <= 0:
            return

        if int(damage) > int(HP):
            setNpcHP(attackedID,0)
        else:
            setNpcHP(attackedID,int(HP - damage))
        npcName = getNpcName(attackedID)
        createNPCMapMessage(attackedID,str(damage),color)
        if addsAggro == True:
            addAggro(attackedID,playerID,damage)
        if spellName == '':
            sendPacketToPlayer(genMessage("You hit a " + str(npcName) + " for " + str(damage) + " damage.",4,color,True),playerID)
        else:
            sendPacketToPlayer(genMessage("Your " + str(spellName) + " hit a "  + str(npcName) + " for " + str(damage) + " damage.",4,color,True),playerID)
    elif PcOrMob == 1 and int(mapData["moral"]) < 2 :
        print "attacking player"
        HP = getPlayerHP(attackedID)
        if HP <= 0:
            return
        if int(damage) > int(HP):
            setPlayerHP(attackedID,0)
        else:
            setPlayerHP(attackedID,int(HP - damage))
        attackedName = getPlayerName(attackedID)
        attackerName = getPlayerName(playerID)
        createPlayerMapMessage(attackedID,str(damage),color)
        if spellName == '':
            sendPacketToPlayer(genMessage("You hit " + str(attackedName) + " for " + str(damage) + " damage.",4,color,True),playerID)
            sendPacketToPlayer(genMessage(str(attackerName) + " hit you for " + str(damage) + " damage.",4,color,True),attackedID)
        else:
            sendPacketToPlayer(genMessage("Your " + str(spellName) + " hit "  + str(attackedName) + " for " + str(damage) + " damage.",4,color,True),playerID)
            sendPacketToPlayer(genMessage(str(attackerName) + "'s " + str(spellName) + " hit you for " + str(damage) + " damage.",4,color,True),attackedID)
    else:
        #sendPacketToPlayer(genMessage("You have nothing to attack.",4,'#ffffff',True),playerID)
        return
    print "sending attack Animation"
    #sendToAllOnMap(genPlaySound(1))
    if attackAnimation == True and curHP > 0:
        sendToAllOnMap(genAttackAnimation(playerID))


def genAttackAnimation(playerID,atkSpeed = 1000):
    packet = {}
    packet["type"] = 116
    packet["player_id"] = int(playerID)
    packet["speed"] = int(atkSpeed)
    return json.dumps(packet)

def genMobAttackAnimation(mobSlotID,atkSpeed = 1000):
    global mapID
    packet = {}
    packet["type"] = 117
    packet["map_id"] = mapID
    packet["slot_id"] = int(mobSlotID)
    packet["speed"] = int(atkSpeed)
    return json.dumps(packet)


def playerSwingFront(playerID):
    global playerData
    global mapData
    global mapNPCs
    playerIndex = playerIDToIndex(playerID)
    if playerIndex > -1:
        x = playerData[playerIndex]["pos"]["x"]
        y = playerData[playerIndex]["pos"]["y"]
        d = playerData[playerIndex]["pos"]["dir"]
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
            for i in range(20):
                if int(mapNPCs[i]["npc_id"]) > -1 and int(mapNPCs[i]["vitals"]["hp"]) > 0:
                    if mapNPCs[i]["pos"]["x"] == x and mapNPCs[i]["pos"]["y"] == y:
                        return (2,i)
        if int(mapData["moral"]) == 1:
            for i in range(len(playerIDList)):
                if playerData[i]["vitals"]["hp"] > 0:
                    if playerData[i]["pos"]["x"] == x and playerData[i]["pos"]["y"] == y:
                        return (1,playerIDList[i])
    return (-1,-1)


def swingFront(x,y,d):
    global playerData
    global mapData
    global mapNPCs
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
        for i in range(20):
            if int(mapNPCs[i]["npc_id"]) > -1 and int(mapNPCs[i]["vitals"]["hp"]) > 0:
                if mapNPCs[i]["pos"]["x"] == x and mapNPCs[i]["pos"]["y"] == y:
                    return (2,i)
    if mapData["moral"] == 1:
        for i in range(len(playerIDList)):
            if playerData[i]["vitals"]["hp"] > 0:
                if playerData[i]["pos"]["x"] == x and playerData[i]["pos"]["y"] == y:
                    return (1,i)
    return (-1,-1)

def getMapID():
    global mapID
    return mapID

def sendToAllOnMap(packetToSend,excluded = None):
    global playerIDList
    if packetToSend != None and packetToSend != "":
        for i in range(len(playerIDList)):
            if excluded == None or int(excluded) != int(playerIDList[i]):
                sendPacketToPlayer(packetToSend,playerIDList[i])

def spawnCharacter(playerID):
    global playerData

    playerIndex = int(playerIDToIndex(playerID))
    if playerIndex > -1:
        sendJson = {}
        sendJson["type"] = 110
        sendJson["player_id"] = playerID
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


def chatMessage(text,channel_id = 0,color = '#ffffff',temp = False):
    return genMessage(text,channel_id,color,temp)

def calculateMaxVitals(playerID):
    playerIndex=playerIDToIndex(playerID)
    if playerIndex > -1:
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
        sendPacketToPlayer(genPlayerVitalMessage(playerID),playerID)

def genPlayerVitalMessage(playerID):
    global playerData
    playerIndex = int(playerIDToIndex(playerID))
    if playerIndex > -1:
        packet = {}
        packet["type"] = 120
        packet["player_id"] = int(playerID)
        packet["vitals"] = playerData[playerIndex]["vitals"]
        packet["max_vitals"] = playerData[playerIndex]["max_vitals"]
        return json.dumps(packet)
    return ''

def genMobVitalMessage(mobID):
    global mapNPCs
    global mobDB
    global mapID
    if mobID > -1 and mobID < 20:
        mobType=int(mapNPCs[mobID]["npc_id"])
        if mobType > -1:
            packet = {}
            packet["type"] = 121
            packet["map_id"] = mapID
            packet["slot_id"] = mobID
            packet["vitals"] = mapNPCs[mobID]["vitals"]
            packet["max_vitals"] = mobDB[int(mobType)]["vitals"]
            return json.dumps(packet)
    return ''

def genMapItemUpdate(mapSlot,mapItem):
    global mapID
    if mapSlot > -1 and mapSlot < 200:
        packet = {}
        packet["type"] = 112
        packet["map_id"] = mapID
        packet["slot_id"] = mapSlot
        packet["map_items"] = mapItem
        return json.dumps(packet)
    return ''

def createMapEffect(sprite,x = 0,y = 0,speed = 500):
    global mapID
    packet = {}
    packet["type"] = 135
    packet["map_id"] = mapID
    packet["map_effect"] = {}
    packet["map_effect"]["sprite"] = sprite
    packet["map_effect"]["x"] = x
    packet["map_effect"]["y"] = y
    packet["speed"] = speed
    sendToAllOnMap(json.dumps(packet))

def createNPCEffect(npcID,sprite,x = 0,y = 0,speed = 500):
    global mapID
    packet = {}
    packet["type"] = 134
    packet["slot_id"] = int(npcID)
    packet["map_id"] = mapID
    packet["map_effect"] = {}
    packet["map_effect"]["sprite"] = sprite
    packet["map_effect"]["x"] = x
    packet["map_effect"]["y"] = y
    packet["speed"] = speed
    sendToAllOnMap(json.dumps(packet))


def createPlayerEffect(playerID,sprite,x = 0,y = 0,speed = 500):
    global mapID
    packet = {}
    packet["type"] = 133
    packet["player_id"] = int(playerID)
    packet["map_effect"] = {}
    packet["map_effect"]["sprite"] = sprite
    packet["map_effect"]["x"] = x
    packet["map_effect"]["y"] = y
    packet["speed"] = speed
    sendToAllOnMap(json.dumps(packet))


def genPlaySound(sound_id):
    packet = {}
    packet["type"] = 123
    packet["sound_id"] = int(sound_id)
    return json.dumps(packet)

def genMessage(text,channel_id = 0,color = '#ffffff',temp = False):
    packet = {}
    packet["type"] = 114
    packet["channel_id"] = channel_id
    packet["color"] = color
    packet["temp"] = temp
    packet["text"] = str(text)
    return json.dumps(packet)


def createMapMessage(x,y,text,color = '#ffffff'):
    if x > -1 and y > -1 and y < 12 and x < 12:
        packet = {}
        packet["type"] = 130
        packet["map_id"] = mapID
        packet["map_text"] = {}
        packet["map_text"]["text"] = text
        packet["map_text"]["color"] = color
        packet["map_text"]["x"] = x
        packet["map_text"]["y"] = y
        sendToAllOnMap(json.dumps(packet))

def createPersonalMapMessage(playerID,x,y,text,color = '#ffffff'):
    if x > -1 and y > -1 and y < 12 and x < 12:
        packet = {}
        packet["type"] = 130
        packet["map_id"] = mapID
        packet["map_text"] = {}
        packet["map_text"]["text"] = text
        packet["map_text"]["color"] = color
        packet["map_text"]["x"] = x
        packet["map_text"]["y"] = y
        sendPacketToPlayer(json.dumps(packet),playerID)


def createPlayerMapMessage(targetID,text,color = '#ffffff'):
    packet = {}
    packet["type"] = 131
    packet["map_id"] = mapID
    packet["player_id"] = targetID
    packet["map_text"] = {}
    packet["map_text"]["text"] = text
    packet["map_text"]["color"] = color
    packet["map_text"]["x"] = 0
    packet["map_text"]["y"] = 0
    sendToAllOnMap(json.dumps(packet))


def createNPCMapMessage(targetID,text,color = '#ffffff'):
    packet = {}
    packet["type"] = 132
    packet["map_id"] = mapID
    packet["slot_id"] = targetID
    packet["map_text"] = {}
    packet["map_text"]["text"] = text
    packet["map_text"]["color"] = color
    packet["map_text"]["x"] = 0
    packet["map_text"]["y"] = 0
    sendToAllOnMap(json.dumps(packet))

#{"type":132,"map_id":969,"slot_id":2,"map_text":{"text":"13","color":"#ff0000","x":0,"y":0}}

def reloadCharacterPacket(playerID):
    playerIndex = int(playerIDToIndex(playerID))
    if playerIndex > -1:
        packet = {}
        packet["type"] = 109
        packet["player_id"] = playerID
        packet["player"] = deepcopy(playerData[playerIndex])
        packet["player"]["data"] = []
        sendPacketToPlayer(json.dumps(packet),playerID)

def genExpMessage(playerID,exp):
    packet = {}
    packet["type"] = 137
    packet["player_id"] = int(playerID)
    packet["exp"] = int(exp)
    return json.dumps(packet)

def genInventoryUpdate(playerID,slotID):
    global playerData
    playerIndex = int(playerIDToIndex(playerID))
    if playerIndex > -1:
        packet = {}
        packet["type"] = 119
        packet["player_id"] = int(playerID)
        packet["slot_id"] = int(slotID)
        packet["inv"] = playerData[playerIndex]["inv"][slotID]
        return json.dumps(packet)
    return ''

def tileFree(x,y):
    global mapNPCs
    global playerData
    global mapData
    if x < 0 or x > 11 or y < 0 or y > 11:
        return False
    for i in range(len(mapNPCs)):
        if int(mapNPCs[i]["npc_id"]) > -1 and mapNPCs[i]["vitals"]["hp"] > 0:
            if mapNPCs[i]["pos"]["x"] == x and mapNPCs[i]["pos"]["y"] == y:
                return False
    for i in range(len(playerData)):
        if playerData[i]["vitals"]["hp"] > 0:
            if playerData[i]["pos"]["x"] == x and playerData[i]["pos"]["y"] == y:
                return False
    tileType = mapData["tiles"][x][y]["type"]
    tileData = mapData["tiles"][x][y]["data"]
    if (tileType == 0 or tileType == 2 or (tileType >= 4 and tileType <= 9) or tileType == 17 or (tileType >= 10 and tileType <= 14) or (tileType == 15 and tileData["blocked"] == False)):
        return True
    return False

def openDoor(xPos,yPos,duration = 10,refreshTimer = False):
    global mapDoors
    global mapID
    global mapMeta
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
        sendToAllOnMap(genMapDoors())
        return True

def genMapDoors():
    global mapDoors
    global mapID
    packet = {}
    packet["type"] = 122
    packet["map_id"] = mapID
    packet["map_doors"] = mapDoors
    return json.dumps(packet)


def shootProjectile(shooterType,shooterID,x,y,d,itemID):
    global mapShots
    freeSlot = freeProjectileSlot()
    if shooterType > -1 and shooterType < 3 and freeSlot > -1:
        mapShot = {}
        mapShot["shooter_type"] = shooterType
        mapShot["shooter_id"] = shooterID
        mapShot["item_id"]  = itemID
        mapShot["pos"] = {}
        mapShot["pos"]["x"] = x
        mapShot["pos"]["y"] = y
        mapShot["pos"]["dir"] = d
        mapShot["pos"]["map_id"] = 0
        
        mapMeta["shots"][freeSlot]["x"] = x
        mapMeta["shots"][freeSlot]["y"] = y

        mapMeta["shots"][freeSlot]["movesLeft"] = itemDB[itemID]["data"]["tile_range"]
        if shooterType == 1:
            rangedItem = getInventorySlotItemID(shooterID,1)
            if rangedItem != itemID:
                mapMeta["shots"][freeSlot]["movesLeft"] = itemDB[rangedItem]["data"]["tile_range"]
        mapShots[freeSlot] = mapShot
        genMapShot(freeSlot,mapShot)
        if shooterType == 1:
            sendToAllOnMap(genAttackAnimation(shooterID))
        elif shooterType == 2:
            sendToAllOnMap(genMobAttackAnimation(shooterID))

def freeProjectileSlot():
    global mapShots
    for i in range(len(mapShots)):
        if mapShots[i]["shooter_type"] == 0:
            return i
    return -1

def genMapShot(mapSlot,mapShot):
    global mapShots
    packet = {}
    packet["type"] = 126
    packet["map_id"] = mapID
    packet["slot_id"] = mapSlot
    packet["map_shots"] = mapShot
    sendToAllOnMap(json.dumps(packet))


def sendPacketToPlayer(packetToSend,playerID):
    global scriptPackets
    if packetToSend != None and packetToSend != '':
        if scriptPackets.has_key(str(playerID)):
            scriptPackets[str(playerID)].append(packetToSend)
        else:
            scriptPackets[str(playerID)] = []
            scriptPackets[str(playerID)].append(packetToSend)
