import alix
from alix import Alix
from pymongo import MongoClient
import json
import datetime

# this micro service store messages into mongodb
# set db and collection parameters
# > alix setParam [service_name] db [db_name]
# > alix setParam [service_name] collection [collection_name]

class MicroService(Alix):
	def onMessage(self, message):
		#save message into mongo
		client = MongoClient()
		db = client[self.getParam('db')]
		collection = db[self.getParam('collection')]
		collection.insert_one({'_timestamp' : datetime.datetime.now(), 'message' : json.loads(message)})
