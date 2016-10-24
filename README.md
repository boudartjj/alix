# Alix, the tiny micro service platform for Python
Alix is a very simple micro services platform for Python for Linux. It is a publish-subscribe micro service architecture based on the Redis message broker.
All classes that implements the Alix class:
- have the onMessage method executed each time a message is sent to the channel they are listening to
- are supported by the Alix platform (start, stop, status)

INSTALL ALIX
- install Redis (http://redis.io/download)
- type the following command: pip install https://github.com/boudartjj/alix/archive/v0.3-alpha.tar.gz

CREATE AND START A NEW MICRO SERVICE
- copy the skeleton_ms.py (https://github.com/boudartjj/alix/tree/master/services) file and implement you code in the onMessage(message) method
    - cp skeleton_ms.py my_ms.py
    - implement your code in the onMessage method (see examples: https://github.com/boudartjj/alix/tree/master/services)
- register, start and test your service
    - start python
    - in python:
        - import alix
        - alix.register('myMicroservice', 'myMicroservice:myMessage', '/home/alix/my_ms.py', 'this is a short description of my micro service')
        - alix.start('myMicroservice')
        - alix.sendMessage('myMicroservice:myMessage', 'Hello, World!'):
