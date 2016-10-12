# Alix, the tiny micro service platform for Python
Alix is a very simple micro services platform for Python. It is a publish-subscribe micro service architecture based on the Redis message broker.
All classes that implements the Alix class:
- have the onMessage method executed each time a message is sent to the channel they are listening to
- are supported by the Alix platform (start, stop, status)

INSTALL ALIX
- install Redis (http://redis.io/download)
- install redis-py (https://pypi.python.org/pypi/redis)
- copy alix files in your microservices folder (i.e. /home/myuser/alix)
- include your microservices folder in PYTHONPATH
    - export PYTHONPATH=${PYTHONPATH}:/home/myuser/alix

CREATE AND START A NEW MICRO SERVICE
- copy the skeleton_ms.py file and implement you code in the onMessage(message) method
    - cp skeleton_ms.py my_ms.py
    - implement your code in the onMessage method
- register, start and test your service
    - start python
    - in python:
        - import alix
        - alix.add('myMicroservice', 'myMicroservice:myMessage', '/home/alix/my_ms.py','/home/alix/my_ms.config' , 'this is a short description of my micro service')
        - alix.start('myMicroservice')
        - alix.sendMessage('myMicroservice:myMessage', 'Hello, World!'):

AVAILABLE METHODS
- register(name, channel, cmd, config='', description='')
    - register a new microservice to the platform
    - parameters
        - name: micro service name
        - channel: name of the channel the service is listening
        - cmd: microservice python file path
        - config: microservice config file path (optional)
        - description: microservice description (optional)
- unregister(name)
    -unregister microservice
    - parameters
        - name: micro service name
- rename(oldName, newName)
    -rename microservice
    - parameters
        - oldName: micro service old name
        - newName: micro service new name
- clone(sourceName, newName)
    -clone microservice
    - parameters
        - sourceName: micro service source name
        - newName: micro service new name
- status(name)
    - get microservice status
    - parameters
        - name: micro service name   
- start(name)
    - start microservice
    - parameters
        - name: micro service name   
- stop(name)
    - stop microservice
    - parameters
        - name: micro service name
- list()
    - returns the list of registered microsevices
- sendMessage(channel, message)
    - send a message to the bus channel
    - parameters
        - channel: name of the channel
        - message: message that will be sent to the channel
