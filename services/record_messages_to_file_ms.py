import alix
from alix import Alix

class MicroService(Alix):
	def onMessage(self, message):
		#save error message into file
		fo = open(self.getParam('path'), 'a')
		fo.write(message + '\n')
		fo.close() 
