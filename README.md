Alix, the tiny microservice platform for Python
===============================================
Alix is a very simple microservices Python platform for Linux. It is a publish-subscribe microservice architecture based on the Redis message broker.
All classes that implements the Alix class:
- have the onMessage method executed each time a message is sent to the channel they are listening to
- send to the output channel the return value of the onMessage method
- are supported by the Alix platform (list, start, stop, info... use alix help to get commands list)

With Alix creating a micro service is as simple as that:
--------------------------------------------------------
```
ping_ms.py

from alix import Alix
class MicroService(Alix):
    #onMessage is executed each time a message is sent to the channel the service is listening to
    def onMessage(self, message):
        #implement your code here
        
        #the return value will be sent to the output channel of the service
        return "pong " + message
```

```
    alix register 'ping' 'pingchannel' 'ping_ms', '/home/myuser/alix' 'this is ping micro service'
    alix start 'ping'
    alix list
    alix sendMessage 'pingchannel' 'my message'
```

INSTALL ALIX
------------
- install Redis (standard installation http://redis.io/download or Docker https://hub.docker.com/_/redis/)
- switch to root user
```
    sudo su
```
- install alix python package
```
    pip install https://github.com/boudartjj/alix/archive/v0.5-alpha.tar.gz
```
- install alix server
```
    wget https://raw.githubusercontent.com/boudartjj/alix/master/bin/alix-srv
    chmod 755 alix-srv
    mv alix-srv /usr/bin
```
- install alix daemon
```
    wget https://raw.githubusercontent.com/boudartjj/alix/master/bin/alixd
    chmod 755 alixd
    mv alixd /etc/init.d
```
- install alix cli
```
    wget https://raw.githubusercontent.com/boudartjj/alix/master/bin/alix
    chmod 755 alix
    mv alix /usr/bin
```

CREATE AND START A NEW MICROSERVICE
-----------------------------------
- start alix daemon
```
    service alixd start
```
- create a folder for your microservices
```
    mkdir /home/myuser/alix
```
- copy the skeleton_ms.py (https://github.com/boudartjj/alix/blob/master/services/skeleton_ms.py) file in your microservices folder and implement you code in the onMessage(message) method
```
    cp skeleton_ms.py my_ms.py
```
- implement your code in the onMessage method (see examples: https://github.com/boudartjj/alix/tree/master/services)
 
- register, start and test your service
```
    alix register 'myMicroservice' 'myMicroservice:myMessage' 'my_ms', '/home/myuser/alix' 'this is a short description of my microservice'
    alix start 'myMicroservice'
    alix list
    alix sendMessage 'myMicroservice:myMessage' 'Hello, World!'
```
