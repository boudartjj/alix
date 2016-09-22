import redis
import subprocess
from subprocess import Popen
import os, signal

def add(name, cmd):
	r = redis.StrictRedis()
	r.set('alix:name:' + name, name)
	r.set('alix:cmd:' + name, cmd)

def getCommand(name):
	r = redis.StrictRedis()
	return r.get('alix:cmd:' + name)

def remove(name):
        r = redis.StrictRedis()
	r.delete('alix:name:' + name)
	r.delete('alix:cmd:' + name)

def start(name):
	cmd = getCommand(name)
	p = Popen(['python', cmd, name], stdout=subprocess.PIPE)
	print ("start " + name)

def stop(name):
	r = redis.StrictRedis()
	pid = r.get('alix:pid:' + name)
	pid = int(pid)
	r.publish('alix:cmd:' + name, 'stop')
	print ("stop " + name)

def status(name):
	r.redis.StrictRedis()
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
