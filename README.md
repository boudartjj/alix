# Alix, the tiny micro service platform for Python
Alix is a micro services platform for Python. It is based on the Redis message broker.
All classes that implements the Alix class:
- are listening for messages on a defined messages channel 
- have the onMessage method executed each time each time a message is sent to the channel they are listening
- are supported by the Alix platform (start, stop, status)

INSTALL ALIX
- install Redis (http://redis.io/download)
- install redis-py (https://pypi.python.org/pypi/redis)
- copy alix.py and skeleton_ms.py in your python microservices folder

CREATE AND START A NEW MICRO SERVICE
All you have to do is to:
- copy the skeleton_ms.py file and implement you code in the onMessage(message) method
    - cp skeleton_ms.py my_ms.py
- register your service
    - start python
    - in python:
        - import alix
        - alix.add('myMicroservice', 'myMicroservice:myMessage', '/home/alix/my_ms.py','/home/alix/my_ms.config' , 'this is a short description of my micro service')
        - alix.start('myMicroservice')

AVAILABLE METHODS
- add(name, channel, cmd, config='', description='')
    - register a new microservice to the platform
    - parameters
        - name: micro service name
        - channel: name of the channel the service is listening
        - cmd: microservice python file path
        - config: microservice config file path (optional)
        - description: microservice description
- remove(name)
    -unregister microservice
    - parameters
        - name: micro service name   
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
