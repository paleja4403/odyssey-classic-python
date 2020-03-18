# odyssey-classic-python
a python based server to host an odyssey classic (https://odysseyclassic.info) server for an HTML5 based client.


This is my first attempt at learning python, so a lot of the code needs refactoring and rework but the server works as is.

Requires Python 3 for autobahn (websocket server)
Requires Python 2.7 for the accountserver, mapserver and scheduler



How it works:

The server is also an attempt at microservices for a game server. I'm using redis to store the states and multiple smaller servers that can be shutdown and scalled out depending on the demand.

There are 4 main server types:

1) webSocketServer.py
2) scheduler.py
3) mapServer.py
4) accountHandler.py

The webSocketServer.py - server's job is to manage connections coming into the server. This server will read packets from autobahn and pass them onto a redis queue for the scheduler to figure out which server (accountHandler or mapServer) needs to process it. This server also listens to a redis queue to kick back messages to the connecting client

scheduler.py - This will figure out where to send the packets it receives and has another thread listening for 'poke' requests. These "poke" requests are ways to queue up a mapServer incase there is no traffic but there is still work to be done.

accountHandler.py - This actually serves 2 purposes. 1) to handle account creations and logins  2) to save everything into the database. It will also load values out of the database if it doesn't exist within redis

mapServer.py - This is where all of the heavy lifting is done. this will check if there are packets for a specific map; it will attempt to aquire a lock on that map, so no other map servers will jump in the middle, process all of the packets and then save the states back into redis and release the lock. If a map server dies mid-run the current packets that were popped will be lost; but the lock will automatically release after a few seconds. Scripting is done using the game.py module that must be included with the mapServer.py.


