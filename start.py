import redis
import time
import json
import alix

r = redis.StrictRedis()
p = r.pubsub()
p.subscribe('micserv')

while True:
	event = p.get_message()
	if event and event['type'] == 'message':
		data = event['data']
		print(data)
		datajs = json.loads(data)
		command = datajs['command']
		if command == 'add':
			name = datajs['name']
			path = datajs['path']
			alix.add(name, path)
		elif command == 'remove':
                        name = datajs['name']
			alix.remove(name)
		elif command == 'start':
                        name = datajs['name']
			alix.start(name)
		elif command == 'stop':
                        name = datajs['name']
			alix.stop(name)
		elif command == 'status': 
                        alix.name = datajs['name']
		elif command == 'list':
			alix.list()
	time.sleep(0.01)
