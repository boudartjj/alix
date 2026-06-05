#this class is micro service skeleton

from urllib import response
import requests
import json
from alix.core import Alix
from alix.core import getParam

class MicroService(Alix):
	def onMessage(self, message):
		print(f'{self.name} received message: {message}')
		
		bot_token = getParam(self.name, 'bot_token')
		chat_id = getParam(self.name, 'chat_id')
		#envoi le message à l'api de telegram et retourne la réponse

		url = "https://api.telegram.org/bot" + bot_token + "/sendMessage"

		data = {
			"chat_id": getParam(self.name, 'chat_id'),	
			"text": message
		}

		response = requests.post(url, data=data)	

		print(f'{self.name} received response: {response.json()}')	

		return response.json()
