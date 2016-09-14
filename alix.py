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

def start(name):
	cmd = getCommand(name)
	p = Popen(['sh', cmd], stdout=subprocess.PIPE)
	r = redis.StrictRedis()
	r.set('alix:pid:' + name, p.pid)
	print ("start " + name + ' - ' + str(p.pid))

def stop(name):
	r = redis.StrictRedis()
	os.kill(int(r.get('alix:pid:' + name)), signal.SIGKILL)
	r.set('alix:pid:' + name, 0)
	print ("stop " + name)

def status(name):
	print("status " + name)

def list():
	services = []
	r = redis.StrictRedis()
	servicesKeys = r.keys('alix:name:*')	
	for key in servicesKeys:
		name = r.get(key)
		cmd = r.get('alix:cmd:' + name)
		pid = r.get('alix:pid:' + name)
		services.append({'name' : name, 'cmd' : cmd, 'pid' : pid})
	return services
