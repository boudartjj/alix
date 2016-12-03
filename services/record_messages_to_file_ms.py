class MicroService(Alix):
	def onMessage(self, message):
		#record message into file
		fo = open(self.getParam('path'), 'a')
		fo.write(message + '\n')
		fo.close() 
