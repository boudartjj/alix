#!/usr/bin/env python

#this micro service send uplanet events messages to telegram

import sys
import subprocess
from subprocess import Popen
import os, signal
import threading
import redis
import time

def add(name, cmd):
        r = redis.StrictRedis()
        r.set('alix:name:' + name, name)
        r.set('alix:cmd:' + name, cmd)

def getCommand(name):
        r = redis.StrictRedis()
        return r.get('alix:cmd:' + name)

def remove(name):
        stop(name)
        r = redis.StrictRedis()
        r.delete('alix:name:' + name)
        r.delete('alix:cmd:' + name)

def start(name):
        cmd = getCommand(name)
        p = Popen(['python', cmd, name], stdout=subprocess.PIPE)
        print ("start " + name)

def stop(name):
        r = redis.StrictRedis()
        r.publish('alix:cmd:' + name, 'stop')
        print ("stop " + name)

def status(name):
        r = redis.StrictRedis()
        p = r.publish('alix:cmd:' + name, 'status')

def list():
        services = []
        r = redis.StrictRedis()
        servicesKeys = r.keys('alix:name:*')
        for key in servicesKeys:
                name = r.get(key)
                cmd = r.get('alix:cmd:' + name)
                services.append({'name' : name, 'cmd' : cmd})
        return services

class Alix():
	def __init__(self, name):
		self._active = False
		self.name = name
		self.r = redis.StrictRedis()

	def isActive(self):
		return self._active

	def start(self):
		self._active = True
                self.sendMessage('starting')

		tProcess = threading.Thread(target = self.process)
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
        	p = self.r.pubsub()
        	p.subscribe('alix:cmd:' + self.name)

        	while self.isActive():
                	event = p.get_message()
                	if event and event['type'] == 'message':
                        	cmd = event['data']
                        	if cmd == 'stop':
                                	self.stop()
                        	elif cmd == 'status':
                                	self.sendMessage('active')
                	time.sleep(0.001)
		self.sendMessage('listen off')

	def _ping(self):
		self.sendMessage('ping on')
		p = self.r.pubsub()
                p.subscribe('alix:ping')

		while self.isActive():
                        event = p.get_message()
                        if event and event['type'] == 'message':
                        	self.sendMessage('active')
                        time.sleep(0.001)
		self.sendMessage('ping off')

	def sendMessage(self, message):
		print 'alix:msg:' + self.name + ' - ' + message
		self.r.publish('alix:msg:' + self.name, message)

	def process(self):
		return None
