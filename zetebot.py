import json
from threading import Lock

import requests
from ws4py.client.threadedclient import WebSocketClient

from karma import KarmaHandler


class ZeteBot(WebSocketClient):

    botname = 'zetebot'

    def opened(self):
        print "Opened."
        self.id = 0
        self.id_lock = Lock()

    def closed(self, code, reason=None):
        print "Connection was closed."

    def received_message(self, m):
        try:
            message = json.loads(m.data)

            if message.get('user') == self.botname:
                # prevent feedback loops
                return

            if message.get('type') != 'message':
                # we only care about message
                return

            text = message.get('text')

            # Begin feature handling

            # KARMA Changer
            is_karma_write = any(ids in text for ids in ('++', '--', '+-'))
            is_karma_read = text.startswith('!') and len(text) > 1

            if is_karma_read or is_karma_write:
                KarmaHandler('').handle(text)
                return

            # All other features start with 'zetebot'
            if not text.startswith('zetebot '):
                return

            text = text[8:]  # remove 'zetebot' prefix
            channel = message.get('channel')

            # Karma Info
            if text.startswith('karma '):
                karma_user = text.split(' ')[1]
                karma_stats = KarmaHandler(karma_user).get()
                self.send(self.format_message(channel, karma_stats))

        except:
            pass

    def get_id(self):
        with self.id_lock:
            self.id += 1
            print "New id: %i" % self.id
            return self.id

    def format_message(self, channel, text):
        return '{{ "username": "{0}", \
                   "type": "message", \
                   "channel": "{1}", \
                   "text": "{2}", \
                   "id": {3} \
                }}'.format(self.botname, channel, text, self.get_id())

if __name__ == '__main__':
    token = 'xoxb-7691461281-O1Rgv7evcKwx1ndv31CBp7Dd'
    resp = requests.post('https://slack.com/api/rtm.start?token=%s' % token)
    url = json.loads(resp.content)['url']

    ws = ZeteBot(url)
    ws.connect()
    ws.run_forever()
