#this class is micro service skeleton

from urllib import response
from alix.core import Alix
from alix.core import getParam, setParam
import requests
import json
from datetime import datetime
import traceback



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

			conversation_history = getParam(self.name, 'conversation_history')
			if conversation_history == None:
				conversation_history = []
			else:
				conversation_history = json.loads(conversation_history)

			max_conversation_history = int(getParam(self.name, 'max_conversation_history'))
			if max_conversation_history == None:
				max_conversation_history = 20
				setParam(self.name, 'max_conversation_history', max_conversation_history)

			conversation_history.append("timestamp: " + str(datetime.now()) + " - *** Me: " + message + " ***")
			prompt = "long_term_memory: " + long_term_memory + " - short_term_memory: " + short_term_memory + " - ** instructions: " + instructions + " ** - conversation_history: " + json.dumps(conversation_history)

			context_summary_prompt = getParam(self.name, 'context_summary_prompt')
			if context_summary_prompt == None:
				context_summary_prompt = "*** Summarize this conversation so far to maximum " + str(max_context_size) + " characters ***"
			else:
				context_summary_prompt = context_summary_prompt + " - " + "*** IMPORTANT: The size of the summary must not exceed " + str(max_context_size) + " characters ***"

			response_raw = self.openai_request(url, token, model, prompt).json()

			print(f'response_raw: {response_raw}')

			response = response_raw["choices"][0]["message"]["content"].replace('```json', '').replace('```', '')

			print(f'response: {response}')

			conversation_history.append("timestamp: " + str(datetime.now()) + " - Agent: " + response)
			if len(conversation_history) > max_conversation_history:
				print(f'Conversation history exceeded {max_conversation_history} interactions, trimming to the most recent {max_conversation_history // 2} interactions.')
				print(context_summary_prompt)

				#update long term memory
				long_term_memory = self.openai_request(url, token, model, context_summary_prompt + ":" + long_term_memory + short_term_memory + json.dumps(conversation_history)).json()["choices"][0]["message"]["content"]
				setParam(self.name, 'long_term_memory', long_term_memory)

				#update short term memory
				short_term_memory = self.openai_request(url, token, model, context_summary_prompt + ":" + json.dumps(conversation_history)).json()["choices"][0]["message"]["content"]
				setParam(self.name, 'short_term_memory', short_term_memory)

				#reduce conversation history to only the most recent interactions	
				setParam(self.name, 'conversation_history', json.dumps(conversation_history[-(max_conversation_history // 2):]))

				print(f'Conversation history size: {len(conversation_history)}')
			else:
				print(f'Conversation history size: {len(conversation_history)}')
				setParam(self.name, 'long_term_memory', long_term_memory)
				setParam(self.name, 'short_term_memory', short_term_memory)
				setParam(self.name, 'conversation_history', json.dumps(conversation_history))

			return response
		except Exception as e:
			error_details = traceback.format_exc()
			print(f'{self.name} encountered an error: {str(e)}')
			print(f'Error details: {error_details}')
			return "Sorry, I encountered an error while processing your request."
		
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
		
		
