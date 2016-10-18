#!/usr/bin/python

import sys
import traceback
import subprocess
from subprocess import Popen
import os, signal
import threading
import redis
import time
import json

def _save(name, channel, cmd, config, description):
	_saveJSON({'name': name, 'cmd': cmd, 'config': config, 'channel': channel, 'description': description})

def _saveJSON(svc):
	name = svc['name']
        r = redis.StrictRedis()
	r.set('alix:config:' + name, json.dumps(svc))

def _load(name):
	r = redis.StrictRedis()
	return json.loads(r.get('alix:config:' + name))

def _delete(name):
	r = redis.StrictRedis()
	r.delete('alix:config:' + name)

def register(name, channel, cmd, config='', description=''):
	_save(name, channel, cmd, config, description)

def getCommand(name):
	return _load(name)['cmd']

def setCommand(name, command):
	svc = _load(name)
	svc['cmd'] = command
	_saveJSON(svc)

def getChannel(name):
	return _load(name)['channel']

def setChannel(name, channel):
        svc = _load(name)
        svc['channel'] = channel
     	_saveJSON(svc)

def getDescription(name):
	return _load(name)['description']

def setDescription(name, description):
        svc = _load(name)
        svc['description'] = description
        _saveJSON(svc)

def getParams(name):
	svc = _load(name)
	if not 'params' in svc.keys():
		svc['params'] = {}
		_saveJSON(svc)
	return _load(name)['params']	

def getParam(name, param):
	paramValue = None
	params = getParams(name)
	if param in params: paramValue = params[param]
	return paramValue

def setParam(name, param, value):
	svc = _load(name)
	if not 'params' in svc.keys():
		svc['params'] = {}
	svc['params'][param] = value
	_saveJSON(svc)

def delParam(name, param):
	svc = _load(name)
	if 'params' in svc and param in svc['params']: del svc['params'][param]
	_saveJSON(svc)

def clone(sourceName, destinationName):
        r = redis.StrictRedis()
        register(destinationName, getChannel(sourceName), getCommand(sourceName), getDescription(sourceName))

def rename(sourceName, destinationName):
        clone(sourceName, destinationName)
        unregister(sourceName)

def unregister(name):
        stop(name)
	_delete(name)

def start(name):
        cmd = getCommand(name)
	channel = getChannel(name)
        p = Popen(['python', cmd, name, channel], stdout=subprocess.PIPE)
        print ("start " + name)

def stop(name):
        r = redis.StrictRedis()
        r.publish('alix:cmd:' + name, 'stop')
        print ("stop " + name)

def stopAll():
	services = list()
	for svc in services:
		stop(svc['name'])

def startAll():
        services = list()
        for svc in services:
                start(svc['name'])

def status(name):
        r = redis.StrictRedis()
	r.set('alix:status:' + name, 'not active')
	r.publish('alix:cmd:' + name, 'status')
	time.sleep(0.1)
	status = r.get('alix:status:' + name)
	print status

def list():
        services = []
        r = redis.StrictRedis()
        servicesKeys = r.keys('alix:config:*')
        for key in servicesKeys:
                config  = json.loads(r.get(key))
                services.append(config)
        return services

def sendMessage(channel, message):
	r = redis.StrictRedis()
	r.publish(channel, message)

def _getErrorMesssage():
	exc_type, exc_value, exc_traceback = sys.exc_info()
	return repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

class Alix():
	def __init__(self, name, channel):
		self._active = False
		self.name = name
		self.channel = channel

	def isActive(self):
		return self._active

	def start(self):
		self._active = True
                self._sendMessage('starting')

		tProcess = threading.Thread(target = self._run)
		tProcess.start()
		tListner = threading.Thread(target = self._listen)
		tListner.start()
		tPing = threading.Thread(target = self._ping)
                tPing.start()

		self._sendMessage('started')

	def stop(self):
		self._sendMessage('stopping')
		self._active = False

	def getParam(self, param):
		return getParam(self.name, param)

	def setParam(self, param, value):
		setParam(self.name, param, value)

	def _listen(self):
		self._sendMessage( 'listen on')
		r = redis.StrictRedis()
        	p = r.pubsub()
        	p.subscribe('alix:cmd:' + self.name)

        	while self.isActive():
                	event = p.get_message()
                	if event and event['type'] == 'message':
                        	cmd = event['data']
                        	if cmd == 'stop':
                                	self.stop()
                        	elif cmd == 'status':
					r.set('alix:status:' + self.name, 'active')
                                	self._sendMessage('active')
                	time.sleep(0.1)
		p.close()
		self._sendMessage('listen off')

	def _ping(self):
		self._sendMessage('ping on')
		r = redis.StrictRedis()
		p = r.pubsub()
                p.subscribe('alix:ping')

		while self.isActive():
                        event = p.get_message()
                        if event and event['type'] == 'message':
                        	self._sendMessage('active')
                        time.sleep(0.1)
		p.close()
		self._sendMessage('ping off')

	def _sendMessage(self, message):
		sendMessage('alix:msg:' + self.name, message)

	def sendMessage(self, channel, message):
		sendMessage(channel, message)
		self._sendMessage(json.dumps({'timestamp': time.strftime('%Y%m%d%H%M%S', time.gmtime()), 'Type': 'message sent', 'name': self.name , 'message': message}))

	def _run(self):
		self._sendMessage('running')
		r = redis.StrictRedis()
		p = r.pubsub()
		p.psubscribe(self.channel)
		while self.isActive():
			event = p.get_message()
			if event: 
				self._sendMessage(json.dumps({'timestamp': time.strftime('%Y%m%d%H%M%S', time.gmtime()), 'Type': 'message received', 'name': self.name , 'message': str(event)}))
			if event and event['type'] == 'pmessage':
				try: 
					self.onMessage(event['data'])
				except Exception as e:
					strNow = time.strftime('%Y%m%d%H%M%S', time.gmtime()) 
					sendMessage('alix:err:' + self.name, json.dumps({'timestamp':strNow, 'serviceName':self.name, 'errorMessage': _getErrorMesssage()}))
			time.sleep(0.01)
		p.close()
		self._sendMessage('not running')

	def onMessage(self, message):
		return None

cmd = sys.argv[1]
print cmd
if cmd == "list":
	print list()
elif cmd == 'stopAll':
	stopAll()
elif cmd == 'startAll':
	startAll()
elif cmd == 'restartAll':
	stopAll()
	startAll()
