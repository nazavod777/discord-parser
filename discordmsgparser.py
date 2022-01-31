import requests
from os import system
from json import loads
from time import sleep
from ctypes import windll
from sys import stderr
from loguru import logger
from translatepy.translators.google import GoogleTranslate
from msvcrt import getch
from re import search, match
from collections import Counter
from math import ceil

logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")
clear = lambda: system('cls')
print('Telegram Channel - https://t.me/n4z4v0d\n')
windll.kernel32.SetConsoleTitleW('Discord Messages Parser | by NAZAVOD')
gtranslate = GoogleTranslate()

discordtoken = str(input('Enter discord token: '))
parse_type = int(input('Your choice: 1 - parse all chat, 2 - parse one user; 3 - delete duplicates: '))
if parse_type == 1:
	chatid = int(input('Enter chat id: '))
	translate_msgs = str(input('Translate messages? (y/N): '))
	if translate_msgs in ('y', 'Y'):
		what_language = str(input('Enter language (example: Turk): '))
	min_words = int(input('Minimum number of words: '))
else:
	guildid = int(input('Enter guild id: '))
	userid = int(input('Enter user id: '))

session = requests.Session()
session.headers['authorization'] = discordtoken

clear()
def parseallchat():
	r = session.get(f'https://discord.com/api/v9/channels/{chatid}/messages?limit=1')
	lastid = loads(r.text)[0]['id']
	while True:
		try:
			cycle_parsed = 0
			messages = []
			r = session.get(f'https://discord.com/api/v9/channels/{chatid}/messages?before={lastid}&limit=100')
			if r.status_code == 200 and len(loads(r.text)) > 1:
				for usermessage in loads(r.text):
					current_message = str(usermessage['content']).replace('\n', '').replace('\r', '')
					if len(current_message) > 0 and current_message != ' ' and current_message != ' ' and current_message.count(' ') >= min_words-1 and search(r'<.*?>', current_message) == None and match('^[a-zA-Zа-яА-ЯёЁ 0-9 ?.-_!()]+$', current_message) is not None:
							messages.append(current_message+'\n')
							cycle_parsed += 1
					lastid = usermessage['id']
			elif r.status_code == 400:
				raise Exception(str(loads(r.text)['errors']['before']['_errors'][0]['code']))
			elif len(loads(r.text)) <= 1:
				raise Exception('succ_end')
			else:
				raise Exception(str(loads(r.text)))
		except Exception as error:
			if str(error) == 'NUMBER_TYPE_MAX':
				logger.success('Successfully parsed all mesages')
				break
			elif str(error) == 'succ_end':
				logger.success('Successfully parsed all mesages')
				break
			else:
				logger.error(f'Error: {str(error)}')
				continue
		else:
			if len(messages) > 0:
				messages_in_str = "".join(messages)
				with open('msg.txt', 'a', encoding='utf-8') as file:
					file.write(f'{messages_in_str}')
				if translate_msgs in ('y', 'Y'):
					translated_msg = gtranslate.translate(messages_in_str, what_language)
					with open('msg_translated.txt', 'a', encoding='utf-8') as file:
						file.write(f'{translated_msg}')
			logger.success(f'Successfully parsed {cycle_parsed} messages')

def parseoneuser():
	r = session.get(f'https://discord.com/api/v9/guilds/{guildid}/messages/search?author_id={userid}')
	if 'Unknown guild' in r.text:
		logger.error('Uncorrect guild id')
		return('bad')
	try:
		total_results = loads(r.text)['total_results']
	except:
		logger.error(f'Error: {r.text}')
		return('bad')
	messages = []
	for i in range(0, ceil(total_results/25)):
		try:
			cycle_parsed = 0
			while True:
				if i == 0:
					r = session.get(f'https://discord.com/api/v9/guilds/{guildid}/messages/search?author_id={userid}')
				else:
					r = session.get(f'https://discord.com/api/v9/guilds/{guildid}/messages/search?author_id={userid}&offset={i*25}')
				if 'retry_after' in loads(r.text):
					errortext = loads(r.text)['message']
					timetosleep = loads(r.text)['retry_after']
					logger.error(f'Error: {errortext}, sleeping {timetosleep}')
					sleep(timetosleep)
				else:
					break
			for msg in loads(r.text)['messages']:
				current_message = msg[0]['content']
				if len(current_message) > 0 and current_message != ' ' and current_message != ' ' and search(r'<.*?>', current_message) == None and match('^[a-zA-Zа-яА-ЯёЁ 0-9 ?.-_!()]+$', current_message) is not None:
					messages.append(current_message)
					cycle_parsed += 1
			logger.success(f'Successfully parsed {cycle_parsed} messages')
		except Exception as error:
			logger.error(f'Unexpected error: {str(error)}')
	with open('msg.txt', 'a', encoding='utf-8') as file:
		for i in range(len(messages)):
			current_message = messages[::-1][i]
			file.write(f'{current_message}\n')
		logger.success('The work has been successfully completed')

def delete_dup():
	lines_set = set()
	fin = open('msg.txt', "r")
	fout = open('msg_unique.txt', "w")
	for line in fin:
		if line not in lines_set:
			fout.write(line)
		lines_set.add(line)
	fin.close()
	fout.close()
	logger.sucess('The work has been successfully completed')

if parse_type == 1:
	parseallchat()
elif parse_type == 2:
	parseoneuser()
else:
	delete_dup()

print('Press any key to exit...')
getch()
