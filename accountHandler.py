import redis
import time
import json
try:
    import thread
except ImportError:
    import _thread as thread
#import time

import psycopg2

cursor = None
connection = None
try:
    connection = psycopg2.connect(user = "postgres",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "odyssey")

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    #print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    #cursor.execute("SELECT version();")
    #record = cursor.fetchone()
    #print("You are connected to - ", record,"\n")

except (Exception, psycopg2.Error) as error :
    cursor = None
    print ("Error while connecting to PostgreSQL", error)

#pip install psycopg2



wsQSize = {}

DEBUG=1
r = redis.Redis(host='localhost',port=6379,db=0)
compatibleVersions = [ "Build 1982 Beta" ]

items = {}
items["uses"] = 0
items["amount"] = 0
items["item_id"] = -1

inventory = []
for i in range(30):
    inventory.append(items)

vitals = {}
vitals["hp"] = 1
vitals["mp"] = 1
vitals["sp"] = 1

stats = {}
stats["mag"] = 0
stats["spd"] = 0
stats["def"] = 0
stats["str"] = 0

pos = {}
pos["dir"] = 0
pos["x"] = 0
pos["y"] = 0
pos["map_id"] = 0


playerTemplate = {}
playerTemplate["data"] = {}
playerTemplate["quest_log"] = [False * 10]
playerTemplate["inv"] = inventory
playerTemplate["birthdate"] = time.time()
playerTemplate["exp"] = 0
playerTemplate["level"] = 1
playerTemplate["swap_sprite"] = -1
playerTemplate["sprite"] = 0
playerTemplate["profession_id"] = 0
playerTemplate["gender"] = 0
playerTemplate["desc"] = ""
playerTemplate["name"] = ""
playerTemplate["access"] = 0
playerTemplate["color"] = "#d3d3d3"
playerTemplate["killer"] = False
playerTemplate["guild_id"] = -1
playerTemplate["train_points"] = 0
playerTemplate["vitals"] = vitals
playerTemplate["max_vitals"] = vitals
playerTemplate["stats"] = stats
playerTemplate["pos"] = pos


#players Struct

#account Struct
accountTemplate = {}
accountTemplate["ignore_players"] = []
accountTemplate["code"] = ""
accountTemplate["username"] = ""
accountTemplate["email"] = ""
accountTemplate["password"] = ""
accountTemplate["reset_password"] = ""
accountTemplate["reset_date"] = time.time()
accountTemplate["last_login"] = ""
accountTemplate["account_created"] = time.time()
accountTemplate["settings"] = {}
accountTemplate["settings"]["toggle_move_lock"] = False
accountTemplate["settings"]["font_size"] = 2
accountTemplate["settings"]["sound_volume"] = 50
accountTemplate["settings"]["music_volume"] = 50
accountTemplate["settings"]["keep_chat_focus"] = False
accountTemplate["settings"]["keep_chat_channel"] = True
accountTemplate["settings"]["play_transition_sounds"] = True
accountTemplate["settings"]["play_environment_sounds"] = False
accountTemplate["settings"]["toggle_run"] = True
accountTemplate["players"] = [1, 1, 2]
accountTemplate["players"][0] = playerTemplate
accountTemplate["players"][1] = playerTemplate
accountTemplate["players"][2] = playerTemplate

def loadFromDB(content):
    if content=="profession" or content == "quest" or content == "shop" or content == "npc" or content == "item":
        cursor.execute("SELECT resourceData from resources where resourceName = '" + content + "';")
        record = cursor.fetchone()[0]
        return record
    return
    #all junk now?
    if content=="profession":
        #placeholder until DB exists
        cursor.execute("SELECT resourceData from resources where resourceName = '" + content + "';")
        record = cursor.fetchone()[0]
        return record
    elif content == "quest":
        return 
    elif content == "shop":
        return 
    elif content == 'npc':
        return
    elif content == "item":
        return 
    else:
        print("Don't know how to load " + str(content) + " yet...")

def fetchProfessions():
    professions=r.get("professionList")
    if professions == None:
        professions = loadFromDB("profession")
        r.set("professionList",str(professions))
    return json.loads(professions)

def fetchResource(resourceName):
    resources=r.get(str(resourceName) + "List")
    if resources == None:
        resources = loadFromDB(resourceName)
        r.set(str(resourceName) + "List",json.dumps(resources))
        return resources
    else:
        return json.loads(resources)


def unknown(message):
    global DEBUG
    if DEBUG == 1:
        print("message not supported yet")
    return 0

def parseMessage(raw):
    global DEBUG
    parse=raw.split(" ")
    socketID = str(parse[1])
    socketServer = str(parse[0])
    print(" ".join(parse[2:]))
    message = json.loads(" ".join(parse[2:]))
    type=message["type"]
    if DEBUG == 1:
        print message

    switcher = {
        0: accountCreate,
        1: accountLogin,
        2: charDelete,
        3: newChar,
        4: loginChar
    }
    func = switcher.get(type,unknown)
    func(message,socketID,socketServer)

def doesEmailExist(emailAddress):
    global cursor
    SQL = """select count(*) from accounts where lower(accountdata->>'email') = %s"""
    cursor.execute(SQL,(str(emailAddress).lower(),))
    if cursor.fetchone()[0] != 0:
        return True
    else:
        return False

def checkLoginCreds(emailAddress,password):
    global cursor
    SQL = """select count(*) from accounts where lower(accountdata->>'email') = %s and accountdata->>'password' = %s"""
    cursor.execute(SQL,(str(emailAddress).lower(),password))
    if cursor.fetchone()[0] != 1:
        return False
    else:
        return True

def isUsernameAvailable(username):
    global cursor
    SQL = """select count(*) from accounts where %s in (lower(accountdata->'players'->0->>'name'),lower(accountdata->'players'->1->>'name'),lower(accountdata->'players'->2->>'name'),lower(accountdata->'players'->3->>'name'));"""
    nameToCheck = str(username).lower()
    cursor.execute(SQL,(nameToCheck,))
    if cursor.fetchone()[0] == 0:
        return True
    else:
        return False


def fetchAccountDetails(emailAddress,password):
    global cursor
    SQL = """select accountdata from accounts where lower(accountdata->>'email') = %s and accountdata->>'password' = %s"""
    cursor.execute(SQL,(str(emailAddress).lower(),password))
    result = cursor.fetchone()
    if result != None:
        return result[0]

def accountCreate(message,socketID,socketServer):
    global r
    global connection
    global cursor
    print("account created")
    if message.has_key('email') and message.has_key('version') and message.has_key('password'):
        print("has everything")
        if doesEmailExist(message["email"]) == False:
            pID = r.get(str(socketServer) + str(socketID) + "pID")
            if pID == None:
                pID = r.incr("nextpID",1)
                r.set(str(socketServer) + str(socketID) + "pID",pID)
                r.set(str(pID) + "2SID",str(socketServer) + " " + str(socketID))

            accountDetail = accountTemplate
            accountDetail["email"] = message["email"]
            accountDetail["password"] = message["password"]
            pl = r.pipeline()
            pl.set('aD_' + str(pID),json.dumps(accountDetail))
            print("doesemailexist false")
            pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winMessage","message":"Account Created!"}')
            pl.rpush('wsQ' + str(socketServer), str(socketID) + """ {"type":101,"account_id":""" + str(pID) + ""","account":""" + json.dumps(accountDetail) + '}')
            professions=json.dumps(fetchResource("profession")) #fetchProfessions()
            print("professions:" + str(professions))
            pl.rpush('wsQ' + str(socketServer), str(socketID) + """ {"type":102,"profession":""" + str(professions) + "}")
            pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winSelectPlayer","message":""}')
            pl.execute()
            SQL="""INSERT into accounts (accountdata,email) values (%s,%s) ON CONFLICT (email) do UPDATE SET accountdata = EXCLUDED.accountdata;"""
            cursor.execute(SQL,(json.dumps(accountDetail),accountDetail["email"]))
            connection.commit()


def sendWorldData(socketID,socketServer,playerID,mapID,playerData):
    global r
    playerCount = 0
    for i in r.keys('p*2M'):
        playerCount += 1
    motd = r.get('MOTD')
        
    pl = r.pipeline()
    pl.set("p" + str(playerID) + "2M",mapID)
    pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":103,"item":' + json.dumps(fetchResource("item")) + '}')
    pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":104,"npc":' + json.dumps(fetchResource("npc")) + '}' )
    pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":105,"shop":' + json.dumps(fetchResource("shop")) + '}')
    pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":139,"quest":' + json.dumps(fetchResource("quest")) + '}')
    #send Player stuff
    #send map stuff
    pl.rpush('map' + str(mapID) + 'NewPlayers',str(playerID))
    pl.rpush('mapWQ',str(mapID))
#    pl.rpush('wsQ' + str(socketServer), str(socketID) + ' ' + json.dumps(dict(playerData, **{"type":110,"player_id":playerID})))
#    pl.rpush('wsQ' + str(socketServer), str(socketID) + ' ' + json.dumps(dict(playerData["pos"], **{"type":115,"player_id":playerID}))) #{"type":115,"player_id":' + str(playerID) + ',' + json.dumps(playerData["pos"]) + '}')
    if motd != None:
        pl.rpush('wsQ' + str(socketServer), str(socketID) + ' ' + genMessage("MOTD: " + str(motd),0,'#ffffff'))
    pl.rpush('wsQ' + str(socketServer), str(socketID) + ' ' + genMessage("There are " + str(playerCount) + " other players online!",0,'#ffff00'))
    pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winGame","message":""}')
    pl.execute()
    return 0

def charDelete(message,socketID,socketServer):
    global r
    pID = r.get(str(socketServer) + str(socketID) + "pID")
    if pID == None and message.has_key("slot_id"):
        print("ERROR: Client has attempted to create a new character without having an account!")
        r.rpush('wsQ' + str(socketServer), str(socketID) + ' CLOSED')
    else:
        accountData = r.get("aD_" + str(pID))
        slotID = int(message["slot_id"])
        #not sure how it'd be none; but if it is.. kick since there is clearly an error here
        if accountData == None or slotID > 2 or slotID < 0:
            print("ERROR: Client has attempted to create a new character without having an account!")
            r.rpush('wsQ' + str(socketServer), str(socketID) + ' CLOSED')
        else:
            accountData = json.loads(accountData)
            accountData["players"][slotID] = playerTemplate
            r.set("aD_" + str(pID),json.dumps(accountData))
            r.rpush('wsQ' + str(socketServer), str(socketID) + """ {"type":101,"account_id":""" + str(pID) + ""","account":""" + json.dumps(accountData) + '}')
            r.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winSelectPlayer","message":""}')



def loginChar(message,socketID,socketServer):
    global r
    pID = r.get(str(socketServer) + str(socketID) + "pID")
    if pID == None:
        print("ERROR: Client has attempted to create a new character without having an account!")
        r.rpush('wsQ' + str(socketServer), str(socketID) + ' CLOSED')
    else:
        accountData = r.get("aD_" + str(pID))
        #not sure how it'd be none; but if it is.. kick since there is clearly an error here
        if accountData == None:
            print("ERROR: Client has attempted to create a new character without having an account!")
            r.rpush('wsQ' + str(socketServer), str(socketID) + ' CLOSED')
        else:
            accountData = json.loads(accountData)
            slotID=int(message["slot_id"])
            playerData=accountData["players"][slotID]
            if playerData["name"] != "":
                packetToSend = genMessage(str(playerData["name"]) + " has joined!",1,'#696969')
                sendToEveryoneOnline(packetToSend)
                playerData["data"]["nextTick"] = 0
                r.set("pD_" + str(pID),json.dumps(playerData))
                r.rpush('wsQ'+ str(socketServer), str(socketID) + ' {"type":109,"player_id":' + str(pID) + ',"player":' + json.dumps(playerData) + '}')
                r.set("aD_" + str(pID),json.dumps(accountData))
                sendWorldData(socketID,socketServer,pID,int(playerData["pos"]["map_id"]),playerData)
    return 0

def newChar(message,socketID,socketServer):
    global r
    pID = r.get(str(socketServer) + str(socketID) + "pID")
    if pID == None:
        print("ERROR: Client has attempted to create a new character without having an pID!")
        r.rpush('wsQ' + str(socketServer), str(socketID) + ' CLOSED')
    else:
        accountData = r.get("aD_" + str(pID))
        #not sure how it'd be none; but if it is.. kick since there is clearly an error here
        if accountData == None:
            print("ERROR: Client has attempted to create a new character without having an account!")
            r.rpush('wsQ' + str(socketServer), str(socketID) + ' CLOSED')
        else:
            accountData = json.loads(accountData)
            slotID = -1
            for i in range(3):
                if accountData["players"][i]["name"] == "":
                    slotID = i
                    break
            if slotID < 0 or slotID > 2:
                print("No Free Slot!!")
                #r.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winMessage","message":"Could not create character, no free account slot. Please delete a character first"}')
                r.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winSelectPlayer","message":"Could not create character, no free account slot. Please delete a character first"}')
            elif isUsernameAvailable(message["name"]) == False:
                r.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winSelectPlayer","message":"That name is already taken!"}')

            else:
                #TODO: validate name,professionID and gender
                profID = int(message["profession_id"])
                genderID = int(message["gender"])
                professionData = fetchResource("profession")
                newCharacter = accountData["players"][slotID]
                newCharacter["pos"] = professionData[profID]["start_pos"]
                newCharacter["max_vitals"] = professionData[profID]["vitals"]
                newCharacter["vitals"] = newCharacter["max_vitals"]
                newCharacter["stats"] = {}#professionData[profID]["stats"]
                newCharacter["stats"]["mag"] = 0
                newCharacter["stats"]["spd"] = 0
                newCharacter["stats"]["def"] = 0
                newCharacter["stats"]["str"] = 0
                newCharacter["profession_id"] = profID
                newCharacter["name"] = message["name"]
                accountData["username"] = slotID
                packetToSend = genMessage("New player " + str(message["name"]) + " has joined!",1,'#696969')
                sendToEveryoneOnline(packetToSend)

                if genderID == 0:
                    newCharacter["sprite"] = professionData[profID]["sprite_male"]
                else:
                    newCharacter["sprite"] = professionData[profID]["sprite_female"]
                newCharacter["data"]["nextTick"] = 0
                accountData["players"][slotID] = newCharacter
                r.set("pD_" + str(pID),json.dumps(newCharacter))
                del newCharacter["max_vitals"]
                r.rpush('wsQ'+ str(socketServer), str(socketID) + ' {"type":109,"player_id":' + str(pID) + ',"player":' + json.dumps(newCharacter) + '}')
                r.set("aD_" + str(pID),json.dumps(accountData))
                sendWorldData(socketID,socketServer,pID,int(newCharacter["pos"]["map_id"]),newCharacter)

    return 0

def checkLoggedIn(email):
    global r
    pIDList = []
    pl=r.pipeline()
    for key in r.keys('aD_*'):
        pl.get(key)
        pIDList.append(str(str(key).split('_')[1]))
    results = pl.execute()
    if results != None:
        for i in range(len(results)):
            accountDetails = json.loads(results[i])
            if str(accountDetails["email"]).lower() == str(email).lower():
                pID = int(pIDList[i])
                SID = r.get(str(pID) + '2SID')
                if SID == None:
                    if r.get('p' + str(pID) + '2M') == None:
                        return pID
                    else:
                        return -1
                else:
                    return -1
    return 0

def saveMap(mapID, mapData):
    global connection
    global cursor
    cursor.execute("SELECT mapdata from maps where id = '" + mapID + "';")
    record = cursor.fetchone()
    if record == None and mapData != None:
        print "saving map " + str(mapID)
        #print mapData
        SQL="""INSERT INTO maps (mapdata,id) values (%s,%s);"""
        cursor.execute(SQL,(mapData,mapID))
        connection.commit()
    elif mapData != None:
        if json.loads(mapData) != record[0]:
            print "saving map " + str(mapID)
            SQL="""UPDATE maps set mapdata=%s where id = %s;"""
            cursor.execute(SQL,(mapData,mapID))
            connection.commit()
    return 0

def saveResources():
    global connection
    global cursor

    SQL_UPDATE='''UPDATE resources set resourcedata = %s where resourcename = %s;'''
    SQL = """SELECT resourcedata from resources where resourcename = %s"""
    for i in ["profession","quest","shop","npc","item"]:
        result = json.loads(r.get(str(i) + "List"))
        if result != None:
            cursor.execute(SQL,(i,))
            dbResult = cursor.fetchone()[0]
            if dbResult == result:
                print "dbResult is the same as redis for " + str(i)
            else:
                print "dbResult is not the same as redis for " + str(i)
                cursor.execute(SQL_UPDATE,(json.dumps(result),i))
                connection.commit()
                print "updated!"

def saveScripts():
    global r
    global connection
    global cursor
    SQL="""INSERT into scripts (script,name) values (%s,%s) ON CONFLICT (name) do UPDATE SET script = EXCLUDED.script;"""
    for key in r.keys('script_*'):
        scriptData = r.get(key)
        if scriptData != None:
            print "saving script " + str(key)
            cursor.execute(SQL,(scriptData,key))
            connection.commit()

        

def saveMapItems(mapID, mapData):
    global connection
    global cursor
    cursor.execute("SELECT data from mapItems where id = '" + mapID + "';")
    record = cursor.fetchone()
    if record == None and mapData != None:
        print "saving map items " + str(mapID)
        SQL="""INSERT INTO mapItems (data,id) values (%s,%s);"""
        cursor.execute(SQL,(mapData,mapID))
        connection.commit()
    elif mapData != None:
        loadedData = json.loads(mapData)
        if loadedData != record[0]:
            print "updating map items " + str(mapID)
            SQL="""UPDATE mapItems set data = %s where id = %s;"""
            cursor.execute(SQL,(mapData,mapID))
            connection.commit()
    return 0

def saveAllMaps():
    global r
    pl = r.pipeline()
    mapIDs = []
    for key in r.keys('map*Data'):
        mapNum = str(str(key)[3:]).split('D')[0]
        pl.get('map' + str(mapNum) + 'Data')
        pl.get('map' + str(mapNum) + 'Items')
        mapIDs.append(mapNum)
    results = pl.execute()
    for i in range(int(len(results)/2)):
        if results[i*2] != None:
            saveMap(mapIDs[i],results[i*2])
            saveMapItems(mapIDs[i],results[i*2+1])

def saveAllPlayers():
    global r
    global cursor
    global connection
    pl = r.pipeline()
    pIDS = []
    #SQL="""UPDATE accounts set accountdata = %s where email = %s;"""
    SQL="""INSERT into accounts (accountdata,email) values (%s,%s) ON CONFLICT (email) do UPDATE SET accountdata = EXCLUDED.accountdata;"""
    print("saving players...")
    for key in r.keys('aD_*'):
        pID = str(str(key).split('_')[1])
        print("checking pID " + str(pID))
        pl.get('aD_' + str(pID))
        pl.get('pD_' + str(pID))
        pl.get(str(pID) + '2SID')
        pl.get('p' + str(pID) + '2M')
        pIDS.append(pID)
    results = pl.execute()
    if len(results) > 3:
        print ("there were " + str(len(results)) + " scanning..")
        pl = r.pipeline()
        for i in range(len(results) / 4):
            if results[int(i*4)] != None:
                accountData = json.loads(results[int(i*4)])
            else:
                accountData = None
            if results[int((i*4)+1)] != None:
                playerData = json.loads(results[int((i*4)+1)])
            else:
                playerData = None
            if accountData != None and playerData != None:
                for SLOTID in range(3):
                    if playerData["name"] == accountData["players"][SLOTID]["name"]:
                        accountData["players"][int(SLOTID)] = playerData
                        print "Saving slot ID " + str(SLOTID)
                        break
                #TODO: save account to db goes here
                #try:
                cursor.execute(SQL,(json.dumps(accountData),accountData["email"]))
                connection.commit()
                #except:
                #    connection.rollback()
                if results[int((i * 4) + 2)] != None or results[int((i * 4) + 3)] != None:
                    pID = pIDS[i]
                    pl.set('aD_' + str(pID),json.dumps(accountData))
            if results[int((i * 4) + 2)] == None and results[int((i * 4) + 3)] == None:
                print("player needs to be cleaned up..")
                pID = pIDS[i]
                print("cleaning up playerID:" + str(pID))
                pl.delete('aD_' + str(pID))
                pl.delete('pD_' + str(pID))
        pl.execute()
    print("done saving players")

def sendToEveryoneOnline(packetToSend):
    for key in r.keys('p*2M'):
        PID=str(key[1:])[:-2]
        print("key:" + str(key) + " PID:" + str(PID))
        sessionID=r.get(str(PID) + '2SID')
        if sessionID != None:
            print("sending to PID:" + str(PID) + " session(" + str(sessionID) + ")")
            connInfo = sessionID.split(" ")
            socketServer = connInfo[0]
            socketID = connInfo[1]
            r.rpush("wsQ" + str(socketServer),str(socketID) + " " + str(packetToSend))

def genMessage(text,channel_id = 0,color = '#ff00ff',temp = False):
    packet = {}
    packet["type"] = 114
    packet["channel_id"] = channel_id
    packet["color"] = color #"#ff00ff"
    packet["temp"] = temp
    packet["text"] = str(text)
    return json.dumps(packet)

def cleanupDeadSockets():
    global r
    global wsQSize
    checkList = []
    pl = r.pipeline()

    newWsQ = {}
    for key in r.keys('wsQ*'):
        pl.llen(key)
        checkList.append(key)
        if wsQSize.has_key(key):
            newWsQ[key] = wsQSize[key]
    wsQSize = newWsQ

    results = pl.execute()
    for i in range(len(results)):
        if results[i] > 3:
            print "results[" + str(i) + "] " + str(results[i]) + " checkList[" + str(i) + "] " + str(checkList[i])
            if wsQSize.has_key(str(checkList[i])) and int(wsQSize[str(checkList[i])]) <= int(results[i]):
                #Removing socket server players
                print "cleaning up dead socket server..."
                pl = r.pipeline()
                print "getting pids connected to " + str(checkList[i])[3:]
                for SID in r.keys(str(checkList[i])[3:] + '*'):
                   result = r.get(str(SID))
                   print "checking SID:" + str(SID) + " result:",result
                   if result != None:
                       PID = result
                       print "removing SID:" + str(SID) + " and PID:" + str(PID)
                       pl.delete(SID)
                       pl.delete(str(PID) + '2SID')
                       notifyMap = r.get('p' + str(PID) + '2M')
                       if notifyMap != None:
                           print "notifying map " + str(notifyMap) + " removePlayers"
                           pl.rpush('map' + str(notifyMap) + 'removePlayers',PID)
                pl.delete(checkList[i])
                pl.execute()
            else:
                wsQSize[str(checkList[i])] = results[i]
        elif wsQSize.has_key(checkList[i]):
            wsQSize[str(checkList[i])] = 0

def backgroundTasks():
    count = 0
    while True:
        start = int(time.time() * 1000)
        saveAllPlayers()
        #if count == 0:
        saveAllMaps()
        cleanupDeadSockets()
        count = ((count + 1) % 12)
        saveScripts()
        saveResources()
        print "background tasks done. took " + str((time.time() * 1000) - start) + " milliseconds."
        time.sleep(600)

def accountLogin(message,socketID,socketServer):
    global r
    email = ''
    password = ''
    if message.has_key('email') and message.has_key('password'):
        email = message['email']
        password = message['password']
    else:
        r.rpush('wsQ' + str(socketServer), str(socketID) + ' CLOSE')
        return
    pl = r.pipeline() 
    if checkLoginCreds(email,password) == True:
        pID = checkLoggedIn(email)
        if pID > -1:
            #pID = r.get(str(socketServer) + str(socketID) + "pID")
            #accountDetails = fetchAccountDetails(email,password)
            if pID == 0:
                pID = r.incr("nextpID",1)
                print "setting " + str(socketServer) + str(socketID) + "pID" + " = " + str(pID)
                accountDetails = fetchAccountDetails(email,password)
                pl.set('aD_' + str(pID),json.dumps(accountDetails))
            else:
                accountDetails = json.loads(r.get('aD_' + str(pID)))
            pl.set(str(socketServer) + str(socketID) + "pID",str(pID))
            pl.set(str(pID) + "2SID",str(socketServer) + " " + str(socketID)) 
            #pl.set('aD_' + str(pID),json.dumps(accountDetails))
            pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winMessage","message":"Login Successful"}')
            professions=fetchResource("profession") #fetchProfessions()
            pl.rpush('wsQ' + str(socketServer), str(socketID) + """ {"type":102,"profession":""" + json.dumps(professions) + "}")
            pl.rpush('wsQ' + str(socketServer), str(socketID) + """ {"type":101,"account_id":""" + str(pID) + ""","account":""" + json.dumps(accountDetails) + '}')
            pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winSelectPlayer","message":""}')
        else:
            pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winLogin","message":"Account already logged in!"}')
    else:
        pl.rpush('wsQ' + str(socketServer), str(socketID) + ' {"type":100,"win":"winLogin","message":"Incorrect Login"}')

    pl.execute()

thread.start_new_thread(backgroundTasks,())

while True:
    print "Reading messages from accountQueue..."
    tmp=str(r.blpop('accountQueue', 0)[1].decode('utf8'))
    print "Parsing" + str(tmp)
    #try:
    parseMessage(tmp)
#    except Exception as e:
#        print("Error sorting message!!")
#        print(e)
#        pass
