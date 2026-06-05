#this class is micro service skeleton

from urllib import response
from alix.core import Alix
from alix.core import getParam, setParam
import requests
import json
from datetime import datetime

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

			#context = getParam(self.name, 'context')
			#if context == None:  
			#	context = ''

			max_context_size = getParam(self.name, 'max_context_size')
			if max_context_size == None:
				max_context_size = 1000
			else:
				max_context_size = int(max_context_size)
			
			long_term_memory = getParam(self.name, 'long_term_memory')
			if long_term_memory == None:  
				long_term_memory = ''

			short_term_memory = getParam(self.name, 'short_term_memory')
			if short_term_memory == None:  
				short_term_memory = ''

			prompt = "long_term_memory: " + long_term_memory + " - short_term_memory: " + short_term_memory + " - ** instructions: " + instructions + " ** - timestamp: " + str(datetime.now()) + " - ** message: " + message + " **"

			context_summary_prompt = getParam(self.name, 'context_summary_prompt')
			if context_summary_prompt == None:
				context_summary_prompt = "Summarize this conversation so far to approximately " + str(0.4 * max_context_size) + " characters"
			else:
				context_summary_prompt = context_summary_prompt + " - " + "### The size of the summary should be around " + str(0.4 * max_context_size) + " characters."
			
			response = self.openai_request(url, token, model, prompt).json()["choices"][0]["message"]["content"]

			print(f'{response}')

			short_term_memory = short_term_memory + "timestamp: " + str(datetime.now()) + " - " + " *** Me: " + message + " *** - Agent: " + response
			if len(long_term_memory + short_term_memory) > max_context_size:
				print('Memory full ' + str(len(long_term_memory + short_term_memory)) + ' > ' + str(max_context_size) + ', summarizing...')

				#update long term memory
				long_term_memory = self.openai_request(url, token, model, context_summary_prompt + ":" + long_term_memory + short_term_memory).json()["choices"][0]["message"]["content"]
				setParam(self.name, 'long_term_memory', long_term_memory)

				#update short term memory
				short_term_memory = self.openai_request(url, token, model, context_summary_prompt + ":" + short_term_memory).json()["choices"][0]["message"]["content"]
				setParam(self.name, 'short_term_memory', short_term_memory)

				print(f'New memory size: {len(long_term_memory) + len(short_term_memory)}')
			else:
				print(f'Memory size: {len(long_term_memory) + len(short_term_memory)}')
				setParam(self.name, 'long_term_memory', long_term_memory)
				setParam(self.name, 'short_term_memory', short_term_memory)

			return response
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
		
		
