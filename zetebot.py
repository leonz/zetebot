import json
import traceback
from threading import Lock

import requests
from ws4py.client.threadedclient import WebSocketClient

from common import InputMessage
from common import InvalidInputException
from common import NoResponseException
from common import OutputMessage
from config import config
from handler import *


class NotUserMessageException(Exception):
    """ The activity received is not a message. Ignore it. """
    pass


class NotZetebotActivityException(Exception):
    """ The activity received is from zetebot.  Ignore it. """
    pass


class ZeteBot(WebSocketClient):

    def opened(self):
        print "Connection was opened."
        self.id = 0
        self.id_lock = Lock()

    def closed(self, code, reason=None):
        closed_message = 'Connection closed unexpectedly. Reason: %s' % reason
        self.send_response(
            OutputMessage(
                channel=config.debug,
                text=closed_message
            )
        )
        print closed_message

    def received_message(self, m):
        try:
            slack_activity = json.loads(m.data)

            message = self.get_input_message_from_activity(slack_activity)

            handler = self.map_message_to_handler(
                message.text.lower(),
                authorized=message.user_id in EBOARD
            )

            bot_response = handler.handle(message)

            self.send_response(bot_response)

        except (NotUserMessageException, NotZetebotActivityException):
            pass

        except NoResponseException as e:
            print e.message

        except InvalidInputException as e:
            print "InvalidInputException: %s" % e.message

        except Exception:
            # Something actually went wrong.
            trace = traceback.format_exc()
            print trace
            error_response = OutputMessage(
                channel=message.channel,
                text=trace
            )
            self.send_response(error_response)

    @staticmethod
    def get_input_message_from_activity(activity):
        if activity.get('user') == config.botname:
            raise NotZetebotActivityException('Activity was from bot.')
        if activity.get('type') != 'message':
            raise NotUserMessageException('Activity was not a message.')

        return InputMessage(
            user_id=activity['user'],
            channel=activity['channel'],
            text=' '.join(activity['text'].split()).strip()
        )

    @staticmethod
    def map_message_to_handler(text, authorized=False):
        """ Get the associated handler for each input message.

            Remove the word 'zetebot' using [8:] for all handlers
            who expect it to be activated.
        """
        if StoreKnowledgeHandler.identify(text):
            return StoreKnowledgeHandler
        if GetKnowledgeHandler.identify(text):
            return GetKnowledgeHandler
        if StoreQuoteHandler.identify(text):
            return StoreQuoteHandler
        if GetQuoteHandler.identify(text):
            return GetQuoteHandler
        if KarmaStatsHandler.identify(text):
            return KarmaStatsHandler

        # Only if user is in EBOARD
        if authorized:
            if ReminderHandler.identify(text):
                return ReminderHandler

        # Lowest priority
        if UpdateKarmaHandler.identify(text):
            return UpdateKarmaHandler

        raise NotZetebotActivityException()

    def get_id(self):
        with self.id_lock:
            self.id += 1
            return self.id

    def send_response(self, response):
        formatted_response = json.dumps(
            {
                "username": config.botname,
                "type": "message",
                "channel": response.channel,
                "text": response.text,
                "id": self.get_id()
            }
        )
        print "Sending response: %s" % repr(formatted_response)
        self.send(formatted_response)

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
