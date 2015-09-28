from urllib.request import *
from urllib.parse import *
from time import *
import json

class Session:
    last_request = 0

    def __init__(self, key, apiver = '5.37'):
        self.key = key
        self.apiver = apiver

    def request(self, method, **kwargs):
        if self.last_request + 1 > time():
            sleep(1)
        self.last_request = time()
        try:
            kwargs['access_token'] = self.key
            kwargs['v'] = self.apiver
            data = urlencode(kwargs)
            w = urlopen("https://api.vk.com/method/" + method + "?" + data)
            response = json.loads(w.read().decode())
            return response
        except:
            return None


class Refresher:
    def request(self, method, **kwargs):
        return self.session.request(method, **kwargs)

    def getnewmessages(self, count=100):
        response = self.request('messages.get', last_message_id=self.last_message, count=count)
        if response and response['response']['items']:
            self.last_message = response['response']['items'][0]['id']
        return response

    def __init__(self, session):
        self.session = session
        self.last_message = 0
        self.getnewmessages()


