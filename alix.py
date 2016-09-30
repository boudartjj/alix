#!/usr/bin/env python

import sys
import traceback
import subprocess
from subprocess import Popen
import os, signal
import threading
import redis
import time

def add(name, channel, cmd, description=''):
        r = redis.StrictRedis()
        r.set('alix:name:' + name, name)
        r.set('alix:cmd:' + name, cmd)
	r.set('alix:channel:' + name, channel)
	r.set('alix:description:' + name, description)

def getCommand(name):
        r = redis.StrictRedis()
        return r.get('alix:cmd:' + name)

def getChannel(name):
        r = redis.StrictRedis()
        return r.get('alix:channel:' + name)

def remove(name):
        stop(name)
        r = redis.StrictRedis()
        r.delete('alix:name:' + name)
        r.delete('alix:cmd:' + name)
	r.delete('alix:channel:' + name)
	r.delete('alix:status:' + name)
	r.delete('alix:description:' + name)

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
	time.sleep(1)
	status = r.get('alix:status:' + name)
	print status

def list():
        services = []
        r = redis.StrictRedis()
        servicesKeys = r.keys('alix:name:*')
        for key in servicesKeys:
                name = r.get(key)
                cmd = r.get('alix:cmd:' + name)
		channel = r.get('alix:channel:' + name)
		description = r.get('alix:description:' + name)
                services.append({'name' : name, 'cmd' : cmd, 'channel': channel, 'description': description})
        return services

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
                self.sendMessage('starting')

		tProcess = threading.Thread(target = self.run)
		tProcess.start()
		tListner = threading.Thread(target = self._listen)
		tListner.start()
		tPing = threading.Thread(target = self._ping)
                tPing.start()

		self.sendMessage('started')

	def stop(self):
		self.sendMessage('stopping')
		self._active = False

	def _listen(self):
		self.sendMessage( 'listen on')
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
                                	self.sendMessage('active')
                	time.sleep(0.001)
		p.close()
		self.sendMessage('listen off')

	def _ping(self):
		self.sendMessage('ping on')
		r = redis.StrictRedis()
		p = r.pubsub()
                p.subscribe('alix:ping')

		while self.isActive():
                        event = p.get_message()
                        if event and event['type'] == 'message':
                        	self.sendMessage('active')
                        time.sleep(0.001)
		p.close()
		self.sendMessage('ping off')

	def sendMessage(self, message):
		r = redis.StrictRedis()
		r.publish('alix:msg:' + self.name, message)

	def run(self):
		self.sendMessage('running')
		r = redis.StrictRedis()
		p = r.pubsub()
		p.subscribe(self.channel)
		while self.isActive():
			event = p.get_message()
			if event: 
				fo = open('alix.msg', 'a')
                                fo.write(time.strftime('%Y%m%d%H%M%S', time.gmtime()) + ' - message received\n')
				fo.write(time.strftime('%Y%m%d%H%M%S', time.gmtime()) + ' - ' + str(event) + '\n')
				fo.close() 
				self.sendMessage(str(event))
			if event and event['type'] == 'message':
				try: 
					self.onMessage(event['data'])
				except Exception as e:
					fo = open('alix.err', 'a')
					fo.write(time.strftime('%Y%m%d%H%M%S', time.gmtime()) + ' - ' + _getErrorMesssage() + '\n')
					fo.close()
					r.publish('alix:error:' + self.name, str(e))
			time.sleep(0.001)
		p.close()
		self.sendMessage('not running')

	def onMessage(self, message):
		return None
