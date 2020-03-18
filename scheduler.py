import redis
import json
try:
    import thread
except ImportError:
    import _thread as thread
import time

r = redis.Redis(host='localhost',port=6379,db=0)

def sortMessage(raw):
    parse=raw.split(" ")
    socketServer = str(parse[0])
    socketID = str(parse[1])
    print(" ".join(parse[2:]))
    message = json.loads(" ".join(parse[2:]))
    type=message["type"]
    if type >= 0 and type <= 4:
        print("Pushing message to accountQueue")
        r.rpush('accountQueue',raw)
    elif type >= 5:
        playerID=r.get(str(str(socketServer)+str(socketID))+"pID")
        if playerID != None:
            playerMap=r.get("p" + str(playerID) + "2M")
            if playerMap != None:
                print("pushing request onto map queue..")
                r.rpush('map' + str(playerMap) + "Queue",str(playerID) + " " + json.dumps(message))
                print("pushing map request onto mapWQ (mapID:" + str(playerMap) + ")")
                r.rpush('mapWQ',str(playerMap))
            else:
                r.rpush('wsQ' + str(socketServer),str(socketID) + ' CLOSED')
        else:
            print("PLAYER ID NOT FOUND, CLOSING CONNECTION!!")
            #close this connection since we don't have the playerID and they're trying to send map shit
            r.rpush('wsQ' + str(socketServer),str(socketID) + ' CLOSED')

def pokerServer():
    global r
    pokeList = {}
    pokedList = []
    while True:
        PL = r.pipeline()
        PL.lrange('pokeRequests',0,-1)
        PL.delete('pokeRequests',0,-1)
        results = PL.execute()
        if results[0] != None:
            for i in range(len(results[0])):
                tmp = results[0][i]
                mapID = tmp.split(" ")[0]
                pokeTime = tmp.split(" ")[1]
#                if pokeList.has_key(str(mapID)):
#                    if pokeList[str(mapID)] > pokeTime:
                        #print "updating poke time for " + str(mapID)
#                        pokeList[str(mapID)] = pokeTime
#                else:
                pokeList[str(mapID)] = pokeTime
#                    print "new poke for " + str(mapID) + " scheduled for " + str(pokeTime)
        #Pokes deal in milliseconds
        PL = r.pipeline()
        curTime = int(time.time() * 1000)
        for mapID in pokeList:
            if curTime > int(pokeList[mapID]):
                print("poking " + str(mapID))
                PL.rpush('mapWQ',mapID)
                PL.rpush('map' + str(mapID) + 'Task', 'POKED')
                pokedList.append(str(mapID))
        for i in range(len(pokedList)):
            print "deleting " + str(pokedList[i])
            del pokeList[str(pokedList[i])]
        pokedList = []
        PL.execute()
        time.sleep(0.01)

thread.start_new_thread(pokerServer,())

while True:
    print "attempting to read from schedulerQueue.."
    tmp=str(r.blpop('schedulerQueue', 0)[1].decode('utf8'))
    print "sorting:" + str(tmp)
    #try:
    sortMessage(tmp)
    #except:
    #    print("Error sorting message!!")
    #    pass
