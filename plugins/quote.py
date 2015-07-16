import random

from config import config
from plugins import InvalidInputException


class QuoteHandler(object):

    collection = config.db.quote

    @classmethod
    def remember(cls, text):
        """ text: user quote (with "") """
        words = text.split('"')
        user = words[0].lower().strip()
        quote = words[1]

        if not quote:
            raise InvalidInputException()

        if not user:
            user = "A Glorious Zete"

        cls.collection.update(
            {"user": user, "quote": quote},
            {"user": user, "quote": quote},
            upsert=True
        )

        return "Quote of the week, anyone?"

    @classmethod
    def retrieve(cls, user=None):
        result = None
        if user:
            count = cls.collection.find({"user": user.lower()}).count()
            if count:
                skip = random.randint(0, count-1)
                result = cls.collection.find_one(
                    {"user": user.lower()},
                    skip=skip
                )
        else:
            count = cls.collection.find().count()
            if count:
                skip = random.randint(0, count-1)
                result = cls.collection.find_one(skip=skip)

        if result is None:
            return "I can't remember any quotes, too blackout."

        return '>\\"{0}\\" - {1}'.format(
            result.get('quote'),
            result.get('user').title()
        )
