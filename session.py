from urllib.request import *
from urllib.parse import *
from time import *
import cyrylic as crl
import json

def gethashtags(s):
    return [word for word in s.split() if (word and word[0] == '#' and word is not '#')]

def getmethod(cls, func):
    return lambda *args, **kwargs : func(cls, *args, **kwargs)


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
        response = self.session.request(method, **kwargs)
        if (response and not response.get('error', False)):
            return response
        else:
            return None

    def reply(self, user_id, **kwargs):
        kwargs['user_id'] = user_id
        return self.request('messages.send', **kwargs)

    def getswitch(self):
        if (super().__thisclass__ != Requester):
            d = super().getswitch()
        else:
            d = dict()
        d.update(dict([[name, (lambda msg, *args : self.switch[name](self, msg, *args))] for name in self.switch]))
        return d

class Tasker:
    def __init__(self, default):
        self.switch = dict()
        self.updates = []
        self.default = default

    def addswitches(self, *switches):
        for sw in switches:
            self.switch.update(sw)

    def addupates(self, *updates):
        self.updates.extend(updates)

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
        response = self.session.request('groups.getMembers', group_id = -int(self.wall))
        self.permitted_users = set()#response['response']['items'])

    def post(self, msg, *args):
        if msg['user_id'] in self.permitted_users:
            self.request('wall.post', owner_id = self.wall, from_group = 1, message = msg['body'])
            self.reply(msg['user_id'], message='Posted')
        else:
            self.reply(msg['user_id'], message = 'Not permitted')

    switch = {
        crl.post : post,
    }

class Homeworker(Waller):
    def __init__(self, session, group):
        super().__init__(session, group)
        self.group = group

    def update(self, *args, **kwargs):
        response = self.request('wall.get', owner_id = self.group, count = 50)
        if (response):
            items = response['response']['items']
            homework = dict([w, 'unknown\n'] for w in crl.subject.values())
            for it in reversed(items):
                tags = gethashtags(it['text'])
                if len(tags) > 1 and tags[0] == crl.hw:
                    homework[tags[1]] = 'https://vk.com/wall' + str(self.group) + '_' + str(it['id']) + '\n' + asctime(gmtime(float(it['date']))) + '\n' + it['text'] + '\n'
            desclist = []
            for sbj in homework:
                desclist.append(sbj + ' - ' + homework[sbj])
            ndesc = '\n'.join(desclist)
            print(self.session.request('groups.edit', group_id = -int(self.group), description = ndesc))


    switch = Waller.switch.copy()

    switch.update({
        crl.hw : Waller.post
    })

