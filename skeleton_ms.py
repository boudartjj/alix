#!/usr/bin/env python

#this class is micro service skeleton

from alix import Alix

class MicroService(Alix):
	def __init__(self, name, channel):
		Alix.__init__(self, name, channel)

	def onMessage(self, message):
		#implement your code here

#get micro service name
name = sys.argv[1]
#get micro service channel
channel = sys.argv[2]

MicroService(name, channel).start()
