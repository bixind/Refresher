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

print('Refresher has started!')

config = configparse('conf.txt')

key = config.get('key')
frequency = int(config.get('freq', 300))

sesn = Session(config['key'])

mesgr = Messenger(sesn)
hwr = Homeworker(sesn, config['group'])

tasks = Tasker(mesgr.getecho(), [mesgr.getswitch(), hwr.getswitch()], [])


last_update = time()
print('Session initialized')

while (True):
    if (last_update + frequency < time()):
        print(time())
        last_update = int(time())
        tasks.executetasks(mesgr.getnewmessages())
        tasks.update()
    else:
        sleep(1)
