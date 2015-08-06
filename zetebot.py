import json
from threading import Lock

import requests
from ws4py.client.threadedclient import WebSocketClient

import plugins
from config import config


class InvalidInputException(Exception):
    pass


class ZeteBot(WebSocketClient):

    def opened(self):
        print "Connection was opened."
        self.id = 0
        self.id_lock = Lock()

    def closed(self, code, reason=None):
        self.send(
            self.format_message(config.debug, "Zetebot connection closed.")
        )
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
                plugins.KarmaHandler.handle(text)
                return

            # just being nice
            possible_thanks = set((match_text, match_text[:-1]))
            valid_thanks = set(('thanks zetebot', 'thank you zetebot'))
            if possible_thanks.intersection(valid_thanks):
                self.send(self.format_message(
                    message.get('channel'),
                    ":heart:"
                ))

            # All other features start with 'zetebot'
            if not match_text.startswith('zetebot '):
                return

            text = text[8:]  # remove 'zetebot' prefix
            match_text = text.lower()  # remove 'zetebot' prefix
            channel = message.get('channel')

            # Karma Info
            if match_text.startswith('karma '):
                karma_user = text.split(' ')[1]
                karma_stats = plugins.KarmaHandler.get(karma_user)
                self.send(self.format_message(channel, karma_stats))
                return

            # Knowledge Storage
            if match_text.startswith('know that '):
                new_fact = text[10:]
                result = plugins.KnowledgeHandler.learn(new_fact)
                self.send(self.format_message(channel, result))
                return

            # Knowledge Retrieval
            identifiers = ('what is ', 'what are ', 'who is ', 'who are ')
            if any([match_text.startswith(ids) for ids in identifiers]):
                question = ' '.join(match_text.split(' ')[2:])
                result = plugins.KnowledgeHandler.retrieve(question)
                self.send(self.format_message(channel, result))
                return

            # Quote Storage
            if match_text.startswith('remember quote '):
                quotable = text[15:]
                result = plugins.QuoteHandler.remember(quotable)
                self.send(self.format_message(channel, result))
                return

            # Quote Retrieval
            if match_text.startswith('quote'):
                speaker = text[5:].lstrip()
                result = plugins.QuoteHandler.retrieve(user=speaker)
                self.send(self.format_message(channel, result))
                return

            # PRIVILEGED COMMANDS BELOW THIS POINT #
            if message.get('user') not in EBOARD:
                return

            user = message.get('user')

            if match_text.startswith('remind everyone'):
                event = text[16:]
                type_ = 'everyone'
                result = plugins.ReminderHandler.schedule(
                    event,
                    channel,
                    user,
                    type_
                )
                self.send(self.format_message(channel, result))
                return

            if match_text.startswith('remind channel'):
                event = text[15:]
                type_ = 'channel'
                result = plugins.ReminderHandler.schedule(
                    event,
                    channel,
                    user,
                    type_
                )
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
