Alix, the tiny microservice platform for Python
===============================================
Alix is a very simple microservices Python platform for Linux. It is a publish-subscribe microservice architecture based on the Redis message broker.
All classes that implements the Alix class:
- have the onMessage method executed each time a message is sent to the channel they are listening to
- send to the output channel the return value of the onMessage method
- are supported by the Alix platform (list, start, stop, info... use alix help to get commands list)

With Alix creating a micro service is as simple as that:
--------------------------------------------------------
- create a ping_ms.py file with the following code
```
from alix import Alix
class MicroService(Alix):
    #onMessage is executed each time a message is sent to the channel the service is listening to
    def onMessage(self, message):
        #implement your code here
        
        #the return value will be sent to the output channel of the service
        return "pong " + message
```

- register and start your ping service
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
- start alix daemon
```
    service alixd start
```
