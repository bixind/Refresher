from urllib.request import *
from urllib.parse import *
from time import *
from session import *
import json

def configparse(name):
    f = open(name, 'r')
    cnfg = dict()
    for lines in f:
        buf = lines.split()
        cnfg[buf[0]] = buf[1]
    f.close()
    return cnfg


def update(curnses):
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
                w = urlopen("https://api.vk.com/method/messages.send?" + data)
            finally:
                sleep(3)




print('Refresher has started!')

config = configparse('conf.txt')

key = config.get('key')
frequency = int(config.get('freq', 300))

sesn = Session(config['key'])

refr = Refresher(sesn)

response = refr.getnewmessages()

update(sesn)
last_update = time()
print('Session initialized')

while (True):
    if (last_update + frequency < time()):
        last_update = int(time())
        update(sesn)
    sleep(1)
