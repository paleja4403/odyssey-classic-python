import asyncio
import redis
import uuid
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

clients = 0
clientLookup = []

def fire_and_forget(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)
    return wrapped


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        global clients
        print("Client connecting: {0}".format(request.peer))
        clientLookup.append(self)
        self.clientID = clients
        clients += 1
        

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        global r
        try:
            if isBinary:
                self.sendClose()
                return
            else:
                print("Text message received: {0}".format(payload.decode('utf8')))
            print("ClientID: " + str(self.clientID) + " server UUID:" + str(SERVER_UUID) + " payload:" + str(payload))
            r.rpush('schedulerQueue',str(str(SERVER_UUID)+" "+str(self.clientID)+" "+str(payload.decode('utf8'))))
        except:
            print("Would have crashed; being nice right now tho")
            #self.sendClose()
#        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        global clientLookup
        global r
        print("WebSocket connection closed: {0}".format(reason))
        clientLookup[self.clientID] = None
        print("Checking for pID to cleanup")
        pID = r.get(str(SERVER_UUID) + str(self.clientID) + 'pID')
        if pID != None:
            pID = int(pID)
            print("cleaning up...pID=" + str(pID))
            
            mapID = r.get('p' + str(pID) + '2M')
            pl = r.pipeline()
            pl.delete(str(SERVER_UUID) + str(self.clientID) + 'pID')
            pl.delete(str(pID) + '2SID')

            if mapID != None:
                pl.rpush('map' + str(int(mapID)) + 'removePlayers',str(pID))
            print(pl.execute())
            print("pipeline executed!")
@fire_and_forget
def sendResponses():
    global SERVER_UUID
    global clientLookup
    global r
    while True:
        MSG=str(r.blpop('wsQ' + str(SERVER_UUID),0)[1].decode('utf-8'))
        try:
            print("INBOUND MESSAGE:" + str(MSG))
            parsed=MSG.split(" ")
            if parsed[0] != '':
                socket=int(parsed[0])
                if clientLookup[socket] != None:
                    message=" ".join(parsed[1:])
                    if message == "CLOSED":
                        print("Closing clientLookup[" + str(socket) + "]!")
                        clientLookup[socket].sendClose()
                    else:
                        print("Sending Message to Client[" + str(socket) + "]:" + str(message))
                        clientLookup[socket].sendMessage(str.encode(message),False)
                else:
                    print("client[" + str(socket) + "] is already closed and cleaned up...")
        except:
            pass
r = redis.Redis(host='172.17.0.2',port=6379,db=0)
SERVER_UUID=uuid.uuid4()

if __name__ == '__main__':
    factory = WebSocketServerFactory("ws://127.0.0.1:8080")
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    print("SERVER_UUID:" + str(SERVER_UUID))
    print("before run in executor")
    sendResponses()
#handleResponses = loop.run_in_executor(None,sendResponses(),None,None)
    print("after run in executor")
    
    coro = loop.create_server(factory, '0.0.0.0', 8080)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        #handleResponses.cancel()
        loop.close()
