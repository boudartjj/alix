# Alix, the tiny micro service platform for Python
Alix is a very simple micro services Python platform for Linux. It is a publish-subscribe micro service architecture based on the Redis message broker.
All classes that implements the Alix class:
- have the onMessage method executed each time a message is sent to the channel they are listening to
- are supported by the Alix platform (start, stop, status)

INSTALL ALIX
- install Redis (http://redis.io/download)
- install alix:
    - switch to root user
        - sudo su
    - install alix python package
        - pip install https://github.com/boudartjj/alix/archive/v0.4-alpha.tar.gz
    - install alix server
        - wget https://raw.githubusercontent.com/boudartjj/alix/master/bin/alix-srv
        - chmod 755 alix-srv
        - mv alix-srv /usr/bin
    - install alix daemon
        - wget https://raw.githubusercontent.com/boudartjj/alix/master/bin/alixd
        - chmod 755 alixd
        - mv alixd /etc/init.d
    - install alix cli
        - wget https://raw.githubusercontent.com/boudartjj/alix/master/bin/alix
        - chmod 755 alix
        - mv alix /usr/bin

CREATE AND START A NEW MICRO SERVICE
- start alix daemon
    - service alixd start
- create a folder for your micro services
    - mkdir /home/myuser/alix
- copy the skeleton_ms.py (https://github.com/boudartjj/alix/blob/master/services/skeleton_ms.py) file in your micro services folder and implement you code in the onMessage(message) method
    - cp skeleton_ms.py my_ms.py
    - implement your code in the onMessage method (see examples: https://github.com/boudartjj/alix/tree/master/services)
- register, start and test your service
    - alix register 'myMicroservice' 'myMicroservice:myMessage' 'my_ms', '/home/myuser/alix' 'this is a short description of my micro service'
    - alix start 'myMicroservice'
    - alix list
    - alix sendMessage 'myMicroservice:myMessage' 'Hello, World!'
