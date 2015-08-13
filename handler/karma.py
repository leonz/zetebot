from common import InvalidInputException
from common import needs_zetebot
from common import needs_zetebot_cls
from common import NoResponseException
from common import OutputMessage
from config import config


class KarmaHandler(object):
    collection = config.db.karma


class UpdateKarmaHandler(KarmaHandler):

    symbols = ('++', '--', '+-')

    @classmethod
    def identify(cls, text):
        return any(ids in text for ids in cls.symbols)

    @classmethod
    def handle(cls, input_message):
        text = input_message.text

        op_gen = (symbol for symbol in cls.symbols if symbol in text)
        op = op_gen.next()

        username = cls.get_username_from_text(text, op)
        cls.update_karma(username, op)

        raise NoResponseException('Karma updated: %s%s' % (username, op))

    @staticmethod
    def get_username_from_text(text, op):
        words = text.split(' ')
        username_gen = (word for word in words if word.endswith(op))

        try:
            return username_gen.next()[:-2].title()
        except StopIteration:
            # caused by the user using karma improperly (eg. ++name)
            raise InvalidInputException()

    @classmethod
    def update_karma(cls, username, op):
        cls.collection.update(
            {"name": username},
            {"$inc": {op: 1}},
            upsert=True
        )


class KarmaStatsHandler(KarmaHandler):

    @staticmethod
    @needs_zetebot
    def identify(text):
        return text.startswith('karma ')

    @classmethod
    @needs_zetebot_cls
    def handle(cls, input_message):
        text = input_message.text
        username = text[6:]

        plus, minus, meh = 0, 0, 0

        karma_doc = cls.collection.find_one({"name": username.title()})
        if karma_doc:
            plus = karma_doc.get('++', 0)
            minus = karma_doc.get('--', 0)
            meh = karma_doc.get('+-', 0)

        return OutputMessage(
            channel=input_message.channel,
            text='Karma for %s: %i++, %i--, %i+-' % (username, plus, minus, meh)
        )
