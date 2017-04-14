import unittest
import os
import time
from alix import alix
from alix import Alix

class TestAlixMethods(unittest.TestCase):
	serviceName = 'test_svc'
	moduleName = 'test_svc'

	def test_CreateService(self):
		#create class file
		fo = open(self.moduleName + '.py', 'w')
		fo.write('from alix import alix\n')
		fo.write('from alix import Alix\n')
		fo.write('class MicroService(Alix):\n')
		fo.write('\tdef onMessage(self, message):\n')
		fo.write('\t\tif message == \'ping\': alix.sendMessage(\'alix:test\', \'pong\')\n')
		fo.close()

		#register service
		alix.register(self.serviceName, 'alix:unittest', self.moduleName, os.getcwd())
		self.assertTrue(True)

	def test_startService(self):
		alix.start(self.serviceName)
		time.sleep(0.1)
		self.assertEquals(alix.status(self.serviceName), 'running')

	def test_stopService(self):
		alix.stop(self.serviceName)
		time.sleep(0.1)
		self.assertEquals(alix.status(self.serviceName), 'stopped')

if __name__ == '__main__':
	TestAlixMethods.serviceName = 'test_svc'
	TestAlixMethods.moduleName = 'test_svc'
	unittest.main()
