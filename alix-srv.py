#!/usr/bin/env python

import redis
import time
import json
import alix

r = redis.StrictRedis()
p = r.pubsub()
p.subscribe('alix:cmd')

print('alix started')

while True:
	event = p.get_message()
	if event and event['type'] == 'message':
		try:
			data = event['data']
			print(data)
			datajs = json.loads(data)
			command = datajs['command']
			if command == 'add':
				name = datajs['name']
				srvcmd = datajs['srvcmd']
				alix.add(name, srvcmd)
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
				r.publish('alix:msg', alix.list())
			elif command == 'ping':
				r.publish('alix:msg', 'pong')
		except Exception as e:
			r.publish('alix:error', e)
	time.sleep(0.01)

print('alix stopped')
