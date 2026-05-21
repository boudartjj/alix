#this class is micro service skeleton

from alix.core import Alix

class MicroService(Alix):
	def onMessage(self, message):
		print(f'{self.name} received message: {message}')
		return "pong " + message
