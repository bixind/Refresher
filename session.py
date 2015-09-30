from urllib.request import *
from urllib.parse import *
from time import *
import cyrylic as crl
import json

def gethashtags(s):
    return [word for word in s.split() if (word and word[0] == '#' and word is not '#')]


class Session:
    last_request = 0

    def setlastrequest(self, t):
        Session.last_request = t

    def __init__(self, key, apiver = '5.37'):
        self.key = key
        self.apiver = apiver

    def request(self, method, **kwargs):
        if Session.last_request + 1 > time():
            sleep(1)
        self.setlastrequest(time())
        try:
            kwargs['access_token'] = self.key
            kwargs['v'] = self.apiver
            data = urlencode(kwargs)
            w = urlopen("https://api.vk.com/method/" + method + "?" + data)
            response = json.loads(w.read().decode())
            return response
        except:
            return None


class Requester:
    def __init__(self, session):
        self.session = session

    def request(self, method, **kwargs):
        return self.session.request(method, **kwargs)

    def reply(self, user_id, **kwargs):
        kwargs['user_id'] = user_id
        return self.request('messages.send', **kwargs)

    def getswitch(self):
        return dict([[name, (lambda msg, *args : self.switch[name](self, msg, *args))] for name in self.switch])

    def getf(self, func):
        return lambda *args, **kwargs : func(self, *args, **kwargs)


class Tasker:
    def __init__(self, default, switches, updates):
        self.switch = dict()
        self.updates = updates
        self.default = default
        for sw in switches:
            self.switch.update(sw)

    def executetasks(self, response):
        if (response['response']['items']):
            for msg in reversed(response['response']['items']):
                tags = gethashtags(msg['body'])
                if (tags):
                    self.switch.get(tags[0], self.default)(msg, *tags)
                else:
                    self.default(msg, *tags)

    def update(self):
        for upd in self.updates:
            upd()

class Messenger(Requester):
    def getnewmessages(self, count=100):
        response = self.request('messages.get', last_message_id=self.last_message, count=count)
        if response and response['response']['items']:
            self.last_message = response['response']['items'][0]['id']
        return response

    def __init__(self, session):
        super().__init__(session)
        self.last_message = 0
        self.getnewmessages()

    def echo(self, msg, *args):
        self.reply(msg['user_id'], message = msg['body'])

    def getecho(self):
        return lambda msg, **kwargs: Messenger.echo(self, msg, **kwargs)

    switch = {
    }


class Waller(Requester):
    def __init__(self, session, wall):
        super().__init__(session)
        self.wall = wall

    def post(self, msg, *args):
        self.request('wall.post', owner_id = self.wall, from_group = 1, message = msg['body'])
        self.reply(msg['user_id'], message='Posted')

    switch = {
        crl.post : post,
    }

class Grouper(Waller):
    def __init__(self, session, group):
        super().__init__(session, group)
        self.group = group


