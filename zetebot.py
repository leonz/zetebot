import json
from threading import Lock

import requests
from ws4py.client.threadedclient import WebSocketClient

from config import config
from plugins import InvalidInputException
from plugins import karma
from plugins import knowledge
from plugins import quote
from plugins import remind


class ZeteBot(WebSocketClient):

    def opened(self):
        print "Connection was opened."
        self.id = 0
        self.id_lock = Lock()

    def closed(self, code, reason=None):
        print "Connection was closed."

    def received_message(self, m):
        try:
            message = json.loads(m.data)

            if message.get('user') == config.botname:
                # prevent feedback loops
                return

            if message.get('type') != 'message':
                # we only care about message
                return

            text = ' '.join(message.get('text').split()).strip()
            match_text = text.lower()

            # Begin feature handling

            # Karma Modifier
            if any(ids in text for ids in ('++', '--', '+-')):
                karma.KarmaHandler.handle(text)
                return

            # All other features start with 'zetebot'
            if not match_text.startswith('zetebot '):
                return

            text = text[8:]  # remove 'zetebot' prefix
            match_text = text.lower()  # remove 'zetebot' prefix
            channel = message.get('channel')

            # Karma Info
            if match_text.startswith('karma '):
                karma_user = text.split(' ')[1]
                karma_stats = karma.KarmaHandler.get(karma_user)
                self.send(self.format_message(channel, karma_stats))
                return

            # Knowledge Storage
            if match_text.startswith('know that '):
                new_fact = text[10:]
                result = knowledge.KnowledgeHandler.learn(new_fact)
                self.send(self.format_message(channel, result))
                return

            # Knowledge Retrieval
            identifiers = ('what is ', 'what are ', 'who is ', 'who are ')
            if any([match_text.startswith(ids) for ids in identifiers]):
                question = ' '.join(match_text.split(' ')[2:])
                result = knowledge.KnowledgeHandler.retrieve(question)
                self.send(self.format_message(channel, result))
                return

            # Quote Storage
            if match_text.startswith('remember quote '):
                quotable = text[15:]
                result = quote.QuoteHandler.remember(quotable)
                self.send(self.format_message(channel, result))
                return

            # Quote Retrieval
            if match_text.startswith('quote'):
                speaker = text[5:].lstrip()
                result = quote.QuoteHandler.retrieve(user=speaker)
                self.send(self.format_message(channel, result))
                return

            # PRIVILEGED COMMANDS BELOW THIS POINT #
            if message.get('user') not in EBOARD:
                return

            user = message.get('user')

            if match_text.startswith('remind everyone'):
                event = text[16:]
                result = remind.ReminderHandler.schedule(event, channel, user)
                self.send(self.format_message(channel, result))
                return

        except InvalidInputException:
            # A user messed up. Not my problem.
            return
        except Exception as e:
            # Silence all exceptions so that the bot can keep working.
            # It's likely caused by trying to parse malformed input
            result = "Exception: %s" % repr(e)
            self.send(self.format_message(config.debug, result))

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
                }}'.format(config.botname, channel, text, self.get_id())

if __name__ == '__main__':
    global EBOARD

    # Pull the members of E-Board, who have special privileges
    resp = requests.post(
        'https://slack.com/api/groups.info?token=%s&channel=%s' %
        (config.slack_token, 'G04SY76KW')
    )

    EBOARD = json.loads(resp.content)['group']['members']

    resp = requests.post(
        'https://slack.com/api/rtm.start?token=%s' % config.slack_token
    )
    url = json.loads(resp.content)['url']

    ws = ZeteBot(url)
    ws.connect()
    ws.run_forever()
