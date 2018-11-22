import alix
from alix import Alix
from pymongo import MongoClient
import json
import datetime

# this micro service store messages into mongodb
# set db and collection parameters
# > alix setParam [service_name] db [db_name]
# > alix setParam [service_name] collection [collection_name]

def _isJSON(message):
	try:
		json.loads(message)
                return True
        except ValueError as error:
                return False

class MicroService(Alix):
	def onMessage(self, message):
		#save message into mongo
		client = MongoClient()
		db = client[self.getParam('db')]
		collection = db[self.getParam('collection')]
		isJSON = _isJSON(message)
		if isJSON:
			collection.insert_one({'_timestamp' : datetime.datetime.now(), 'isJSON': True, 'message' : json.loads(message)})
		else:
			collection.insert_one({'_timestamp' : datetime.datetime.now(), 'isJSON': False, 'message' : message})
