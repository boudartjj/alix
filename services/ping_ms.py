#this class is micro service skeleton

from alix.core import Alix

class MicroService(Alix):
	def onMessage(self, message):
		return "pong " + message
