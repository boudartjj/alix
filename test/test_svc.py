from alix import alix
from alix import Alix
class MicroService(Alix):
	def onMessage(self, message):
		if message == 'ping': alix.sendMessage('pong')
