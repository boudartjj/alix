# alix
Alix is a micro services framework for Python. It is based on the Redis message broker.

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
