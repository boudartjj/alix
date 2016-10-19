#!/usr/bin/env python

import sys
from alix import Alix

class MicroService(Alix):
	def __init__(self, name, channel):
		Alix.__init__(self, name, channel)

	def onMessage(self, message):
		#save error message into file
		fo = open(self.getParam('path'), 'a')
		fo.write(message + '\n')
		fo.close() 

#get micro service name
name = sys.argv[1]
#get micro service channel
channel = sys.argv[2]

MicroService(name, channel).start()
