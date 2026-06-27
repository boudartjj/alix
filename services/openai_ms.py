#this class is micro service skeleton

from urllib import response
from alix.core import Alix
from alix.core import getParam, setParam
import requests
import json
import ast
import re
from datetime import datetime
import traceback



class MicroService(Alix):
	def onMessage(self, message):
		print(f'{self.name} received message: {message}')

		try:
			## Retrieve parameters from the Alix framework
			url = getParam(self.name, 'url')
			token = getParam(self.name, 'token')
			model = getParam(self.name, 'model')

			instructions = getParam(self.name, 'instructions')
			if instructions == None:
				instructions = ''

			tools = getParam(self.name, 'tools')
			if tools == None:
				tools = []
			else:
				try:
					tools = ast.literal_eval(tools)
					print(f'Tools loaded')
				except json.JSONDecodeError:
					tools = []

			max_context_size = getParam(self.name, 'max_context_size')
			if max_context_size == None:
				max_context_size = 1000
			else:
				max_context_size = int(max_context_size)

			timeout = getParam(self.name, 'timeout')
			if timeout == None:
				timeout = 60
			else:
				timeout = int(timeout)

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

			max_conversation_history = int(getParam(self.name, 'max_conversation_history'))
			if max_conversation_history == None:
				max_conversation_history = 20
				setParam(self.name, 'max_conversation_history', max_conversation_history)

			context_summary_prompt = getParam(self.name, 'context_summary_prompt')
			if context_summary_prompt == None:
				context_summary_prompt = "*** Summarize this conversation so far to maximum " + str(max_context_size) + " characters ***"
			else:
				context_summary_prompt = context_summary_prompt + " - " + "*** IMPORTANT: The size of the summary must not exceed " + str(max_context_size) + " characters ***"

			## build messages 
			messages = [
				{"role": "system", "content": instructions},
				{"role": "system", "content": long_term_memory},
				{"role": "system", "content": short_term_memory}
			]


			# append the saved messages from the conversation history to the messages list
			saved_messages = getParam(self.name, 'messages')
			if saved_messages != None:
				try:
					saved_messages = json.loads(saved_messages)
					messages.extend(saved_messages)
				except json.JSONDecodeError:
					print(f'Error decoding saved messages JSON: {saved_messages}')
					error_details = traceback.format_exc()
					print(f'{self.name} encountered an error during loading saved messages: {str(e)}')
					print(f'Error details: {error_details}') 

			# append the new message
			messages.append({"role": "user", "content": f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {message}"})

			# remove all messages containing tool_call_id attribute
			messages = [
				msg for msg in messages
				if "tool_calls" not in msg and "tool_call_id" not in msg
			]

			can_reply = False
			while not can_reply:
				# send the request to the OpenAI API and get the response
				response_raw = self.openai_request(url, token, model, messages, tools, timeout)

				can_reply = True

				if response_raw is None:
					print(f'{self.name} did not receive a response from the OpenAI API.')
					return "Sorry, I couldn't get a response from the OpenAI API."

				try:
					print(f'response_raw: {response_raw.json()}')
				except Exception as e:
					print(f'Error parsing response JSON: {str(e)}')
					return "Sorry, I received an invalid response from the OpenAI API."

				## Extract the content from the OpenAI API response and update memory
				response = ""
				try:
					response = response_raw.json()["choices"][0]["message"]["content"].replace('```json', '').replace('```', '')
					if len(response) > 0 :
						keep_msg = True
						try:
							keep_msg = json.loads(response)["remember"]
						except:
							pass
						
						messages.append({"role": "assistant", "content": response})
						print(f'response: {response}')
						try:
							self.updateMemory(messages, long_term_memory, short_term_memory, max_conversation_history, context_summary_prompt, url, token, model)
						except Exception as e:
							error_details = traceback.format_exc()
							print(f'{self.name} encountered an error during memory update: {str(e)}')
							print(f'Error details: {error_details}')
				except:
					pass

				## Handle tool calls if any are present in the response
				tool_calls = []
				try:
					tool_calls = response_raw.json()["choices"][0]["message"]["tool_calls"]
					messages.append({"role": "assistant", "content": "", "tool_calls": tool_calls})
					if tool_calls is not None:
						try:
							for tool_call in tool_calls:
								can_reply = False
								module_function = tool_call["function"]["name"]
								if '.' in module_function:
									module_function = module_function.split('.')	
									module = module_function[0]
									function = module_function[1]
								else:
									module = module_function
									function = None	
								params = json.loads(tool_call["function"]["arguments"])
	
								print(f'Calling tool: {module_function} with parameters: {params}')
								tool_response = getattr(__import__(module), function)(**params)
								messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_call["function"]["name"], "content": json.dumps(tool_response)})
						except Exception as e:
							error_details = traceback.format_exc()
							print(f'{self.name} encountered an error: {str(e)}')
							print(f'Error details: {error_details}')
				except:
					pass
				
			print(f'can reply = {can_reply}')

			return json.dumps(clean_json(response), ensure_ascii=False)
		except Exception as e:
			error_details = traceback.format_exc()
			print(f'{self.name} encountered an error: {str(e)}')
			print(f'Error details: {error_details}')
			return "Sorry, I encountered an error while processing your request."
		
	def openai_request(self, url, token, model, messages, tools = [], timeout = 60):			
		headers = {
			"Content-Type": "application/json",
			"Authorization": token
		}

		data = {
			"model": model,
			"messages": messages,
			"tools": tools,
			"stream": False
		}

		resp = None
		try:
			resp = requests.post(url, headers=headers, json=data, timeout=timeout)
		except Exception as e:
			error_details = traceback.format_exc()
			print(f'{self.name} encountered an error during OpenAI API request: {str(e)}')
			print(f'Error details: {error_details}')

		return resp

	def updateMemory(self, messages, long_term_memory, short_term_memory, max_conversation_history, context_summary_prompt, url, token, model):
		## Handle conversation history and memory management

		messages = [msg for msg in messages if msg['role'] in ['user', 'assistant']]

		if len(messages) > max_conversation_history:
			print(f'Conversation history exceeded {max_conversation_history} interactions, trimming to the most recent {max_conversation_history // 2} interactions.')
			print(context_summary_prompt)

			#update long term memory
			response = self.openai_request(url, token, model, context_summary_prompt + ": " + long_term_memory + " - " + short_term_memory)
			if response is not None:
				try:
					response_json = response.json()
					if "choices" in response_json and len(response_json["choices"]) > 0:
						long_term_memory = response_json["choices"][0]["message"]["content"]
						setParam(self.name, 'long_term_memory', long_term_memory)
				except Exception as e:
					print(f'Error updating long term memory: {str(e)}')

			#update short term memory
			response = self.openai_request(url, token, model, context_summary_prompt + ": " + json.dumps(messages))
			if response is not None:
				try:
					response_json = response.json()
					if "choices" in response_json and len(response_json["choices"]) > 0:
						short_term_memory = response_json["choices"][0]["message"]["content"]
						setParam(self.name, 'short_term_memory', short_term_memory)
				except Exception as e:
					print(f'Error updating short term memory: {str(e)}')

			#reduce conversation history to only the most recent interactions	
			setParam(self.name, 'messages', json.dumps(messages[-(max_conversation_history // 2):]))

			print(f'Conversation history size: {len(messages)}')
		else:
			print(f'Conversation history size: {len(messages)}')
			setParam(self.name, 'long_term_memory', long_term_memory)
			setParam(self.name, 'short_term_memory', short_term_memory)

			# save only user and assistant messages to conversation history
			messages = [msg for msg in messages if msg['role'] in ['user', 'assistant']]
			setParam(self.name, 'messages', json.dumps(messages))
		
		return messages, long_term_memory, short_term_memory

def clean_json(s: str) -> any:
    if not s or not isinstance(s, str):
        return s

    s = s.strip()

    # Nettoyer les backticks markdown
    if s.startswith('```'):
        s = '\n'.join(s.split('\n')[1:-1]).strip()

    # Extraire le bloc JSON
    match = re.search(r'\{.*\}|\[.*\]', s, re.DOTALL)
    if match:
        s = match.group(0)

    # Remplacer les sauts de ligne réels DANS les valeurs par \n
    # (entre les guillemets uniquement)
    def escape_newlines(m):
        return m.group(0).replace('\n', '\\n').replace('\r', '\\r')

    s = re.sub(r'"(.*?)"', escape_newlines, s, flags=re.DOTALL)

    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        print(f"JSON error at pos {e.pos}: {e.msg}")

    try:
        parsed = ast.literal_eval(s)
        return json.loads(json.dumps(parsed))
    except (ValueError, SyntaxError):
        pass

    return None