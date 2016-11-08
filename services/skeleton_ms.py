#!/usr/bin/env python

#this class is micro service skeleton

import sys
from alix import Alix

class MicroService(Alix):
	def __init__(self, name):
		Alix.__init__(self, name)

	def onMessage(self, message):
		#implement your code here
		pass

#get micro service name
name = sys.argv[1]

MicroService(name).start()
