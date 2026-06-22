# Microservice example for Telegram messaging
# This service sends received messages to a Telegram chat using a bot token

import requests
import json
from alix.core import Alix
from alix.core import getParam, setParam, getOutputChannel
import time
import traceback

class MicroService(Alix):
	"""Telegram microservice implementation based on the Alix framework."""

	def onMessage(self, message):
		"""Handle incoming messages from the Alix event loop.

		The incoming message is forwarded to the configured Telegram chat.
		"""
		
		if len(message) == 0:
			print(f'{self.name} received empty message, ignoring.')
			return None
		
		print(f'{self.name} received message: {message}')
		
		try:
			message = json.loads(message)

			# Retrieve bot token and chat ID from service parameters
			bot_token = getParam(self.name, 'bot_token')

			# Build Telegram API URL for sending a message
			url_sendMessage = f"https://api.telegram.org/bot{bot_token}/sendMessage"

			data = {
				"chat_id": message.get('chatid'),
				"text": message.get('response')
			}

			# Send the message to Telegram and capture the response
			response = requests.post(url_sendMessage, data=data)

			# Log the Telegram response for diagnostics
			print(f'{self.name} received response: {response.json()}')
		except Exception as e:
			error_details = traceback.format_exc()
			print(f'{self.name} encountered an error: {str(e)}')
			print(f'Error details: {error_details}')

		return None

	def mainLoop(self):
		"""Continuously poll Telegram updates and forward new messages."""
		bot_token = getParam(self.name, 'bot_token')
		
		last_update_id = getParam(self.name, 'last_update_id')
		if last_update_id is None:
			last_update_id = 0

		output_channel = getOutputChannel(self.name)

		# Build Telegram API URL for polling updates
		url_getUpdates = f"https://api.telegram.org/bot{bot_token}/getUpdates"

		while self.isActive():
			try:
				# Poll Telegram for updates
				data = {
					"offset": last_update_id + 1,
					"timeout": 10  # Long polling timeout
				}
				response = requests.get(url_getUpdates, data = data)
				updates = response.json().get('result', [])

				update_id = 0
				for update in updates:
					update_id = update['update_id']

					# Only process new updates once
					if update_id > last_update_id:
						last_update_id = update_id
						result = json.dumps(update)
						print(f'{self.name} received Telegram update: {result}')

						if output_channel is not None:
							self.sendMessage(output_channel, result)
							
				if last_update_id is not None:		
					setParam(self.name, 'last_update_id', update_id)
				
				time.sleep(1)  # Sleep briefly to avoid excessive polling
			except Exception as e:
				error_details = traceback.format_exc()
				print(f'{self.name} encountered an error: {str(e)}')
				print(f'Error details: {error_details}')
