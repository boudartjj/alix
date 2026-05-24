#this class is micro service skeleton

from urllib import response
from alix.core import Alix
from alix.core import getParam
import requests

class MicroService(Alix):
	def onMessage(self, message):
		print(f'{self.name} received message: {message}')

		url = getParam(self.name, 'url')
		token = getParam(self.name, 'token')
		model = getParam(self.name, 'model')
		
		headers = {
    		"Content-Type": "application/json",
    		"Authorization": token
		}

		data = {
			"model": model,
			"messages": [{"role": "user", "content": message}],
			"stream": False
		}
		response = requests.post(url, headers=headers, json=data)

		print(response.json()["choices"][0]["message"]["content"])
		
		return response.json()["choices"][0]["message"]["content"]
