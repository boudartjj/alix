#this class is micro service skeleton

from urllib import response
from alix.core import Alix
from alix.core import getParam, setParam
import requests
import json

class MicroService(Alix):
	def onMessage(self, message):
		print(f'{self.name} received message: {message}')

		try:
			url = getParam(self.name, 'url')
			token = getParam(self.name, 'token')
			model = getParam(self.name, 'model')
			instructions = getParam(self.name, 'instructions')
			if instructions == None:
				instructions = ''
			context = getParam(self.name, 'context')
			if context == None:
				context = ''
			max_context_size = getParam(self.name, 'max_context_size')
			if max_context_size == None:
				max_context_size = 1000
			else:
				max_context_size = int(max_context_size)

			context_summary_prompt = getParam(self.name, 'context_summary_prompt')
			if context_summary_prompt == None:
				context_summary_prompt = "Summarize this conversation so far to approximately " + str(0.75 * max_context_size) + " characters"
			else:
				context_summary_prompt = context_summary_prompt + ". " + "The size of the summary should be around " + str(0.75 * max_context_size) + " characters."
			
			request = "context: " + context + " - instructions: " + instructions + " - ### message: " + message
			response = self.openai_request(url, token, model, request)

			print(f'{response.json()["choices"][0]["message"]["content"]}')

			context = context + "Me: " + message + " - Agent: " + response.json()["choices"][0]["message"]["content"] + " - "
			if len(context) > max_context_size:
				print('Context too long ' + str(len(context)) + ' > ' + str(max_context_size) + ', summarizing...')
				context = self.openai_request(url, token, model, context_summary_prompt + ":" + context)
				print(f'Summarized context size: ' + str(len(context.json()["choices"][0]["message"]["content"])) + ' characters')
				setParam(self.name, 'context', context.json()["choices"][0]["message"]["content"])
			else:
				setParam(self.name, 'context', context)

			return response.json()["choices"][0]["message"]["content"]
		except Exception as e:
			print(f'Error: {e}')
			return f'Error: {e}'
		
	def openai_request(self, url, token, model, request):			
		headers = {
			"Content-Type": "application/json",
			"Authorization": token
		}

		data = {
			"model": model,
			"messages": [{"role": "user", "content": request}],
			"stream": False
		}

		return requests.post(url, headers=headers, json=data)
		
		
