from urllib.request import *
from urllib.parse import *
from time import *
import json

last_message_id = 0

def update():
    global last_message_id
    try:
        data = urlencode({'last_message_id' : last_message_id,
                          'count' : 10,
                          'access_token' : key,
                          'v' : '5.37'
                          })
        w = urlopen("https://api.vk.com/method/messages.get?" + data)
        response = json.loads(w.read().decode())['response']['items']
    except:
        return
    if (response):
        last_message_id = response[0]['id']
        for msg in response:
            try:
		 data = urlencode({'user_id' : msg['user_id'], 'message' : msg['body'], 'access_token' : key, 'v' : '5.37'})
            	 urlopen("https://api.vk.com/method/messages.send?" + data)
	    sleep(3)




print('Refresher has started!')

f = open('conf.txt', 'r')
config = dict()
for lines in f:
    buf = lines.split()
    config[buf[0]] = buf[1]
f.close()

key = config.get('key')
frequency = int(config.get('freq', 300))

data = urlencode({'last_message_id' : last_message_id,
                          'count' : 10,
                          'access_token' : key})
w = urlopen("https://api.vk.com/method/messages.get?" + data)
response = json.loads(w.read().decode())['response'][1:]
if (response):
    last_message_id = response[0]['mid']

update()
last_update = time()
if (key):
    while (True):
        if (last_update + frequency < time()):
            last_update = int(time())
            update()
        sleep(1)
