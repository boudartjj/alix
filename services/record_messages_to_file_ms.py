#!/usr/bin/env python

import sys
from alix import Alix

class MicroService(Alix):
	def __init__(self, name):
		Alix.__init__(self, name)

	def onMessage(self, message):
		#save error message into file
		fo = open(self.getParam('path'), 'a')
		fo.write(message + '\n')
		fo.close() 

#get micro service name
name = sys.argv[1]

MicroService(name).start()
