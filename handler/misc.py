from random import sample

from common import NotZetebotActivityException
from common import OutputMessage
from config import config


class MiscHandler(object):

    thanks = ('thanks', 'thank you')
    hello = ('hello', 'hey', 'hi', 'good morning', 'good afternoon',
             'good evening', 'hola', 'yo', 'greetings')

    hello_response = ('Hi there!', "What's up?", 'Hey!', )

    @classmethod
    def identify(cls, text):
        return config.botname in text.lower()

    @classmethod
    def handle(cls, input_message):
        text = input_message.text.lower()

        message = None

        # thanks!
        if any(words in text for words in cls.thanks):
            message = ':heart:'

        # hello
        if any(words in text for words in cls.hello):
            message = sample(cls.hello_response, 1)

        if message:
            return OutputMessage(
                channel=input_message.channel,
                text=message
            )

        raise NotZetebotActivityException()
