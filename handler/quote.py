import random

from common import InvalidInputException
from common import needs_zetebot
from common import needs_zetebot_cls
from common import OutputMessage
from config import config


class QuoteHandler(object):
    collection = config.db.quote


class StoreQuoteHandler(QuoteHandler):

    @staticmethod
    @needs_zetebot
    def identify(text):
        return text.startswith('remember quote')

    @classmethod
    @needs_zetebot_cls
    def handle(cls, input_message):
        # temporarily block this user
        if input_message.user_id in (u'D09SE2P47'):
            return

        """ text: user quote (with "") """
        words = input_message.text.split('"')
        user = words[0].lower().strip()[15:]
        quote = words[1].strip()

        if not quote:
            raise InvalidInputException()

        if not user:
            user = "A Glorious Zete"

        cls.collection.update(
            {"user": user, "quote": quote},
            {"user": user, "quote": quote},
            upsert=True
        )

        return OutputMessage(
            channel=input_message.channel,
            text="Quote of the week, anyone?"
        )


class GetQuoteHandler(QuoteHandler):

    @staticmethod
    @needs_zetebot
    def identify(text):
        return text.startswith('quote')

    @classmethod
    @needs_zetebot_cls
    def handle(cls, input_message):

        author = input_message.text[5:].lstrip().lower()
        quote_doc = cls._get_random_quote_doc(author=author)

        if not quote_doc:
            message_text = (
                "I can't remember any quotes"
                "%s, too blackout" % (' from ' + author if author else '')
            )
        else:
            message_text = '>\"{0}\" - {1}'.format(
                quote_doc.get('quote'),
                quote_doc.get('user').title()
            )

        return OutputMessage(
            channel=input_message.channel,
            text=message_text
        )

    @classmethod
    def _get_random_quote_doc(cls, author=None):
        count = cls._get_count_of_quotes(author=author)
        if not count:
            return None

        skip = random.randint(0, count-1)

        if author:
            return cls.collection.find_one(
                {"user": author},
                skip=skip
            )
        else:
            return cls.collection.find_one(skip=skip)

    @classmethod
    def _get_count_of_quotes(cls, author=None):
        """ Count the number of quote documents in the table.
            If author is set, only includes their quotes.
        """
        if author:
            return cls.collection.find({"user": author}).count()
        else:
            return cls.collection.find().count()
