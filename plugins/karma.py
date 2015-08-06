from config import config
from zetebot import InvalidInputException


class KarmaHandler(object):

    collection = config.db.karma

    @classmethod
    def handle(cls, text):
        if '++' in text:
            user = cls.grab_user_from_text(text, '++')
            cls.plus(user)
        elif '--' in text:
            user = cls.grab_user_from_text(text, '--')
            cls.minus(user)
        elif '+-' in text:
            user = cls.grab_user_from_text(text, '+-')
            cls.meh(user)
        else:
            raise InvalidInputException()

    @staticmethod
    def grab_user_from_text(text, changer):
        try:
            return [x for x in text.split(' ') if
                    x.endswith(changer)][0][:-2].title()
        except IndexError:
            # caused by the user using karma improperly (eg. ++name)
            raise InvalidInputException()

    @classmethod
    def plus(cls, user):
        cls.collection.update(
            {"name": user},
            {"$inc": {"plus": 1}},
            upsert=True
        )

    @classmethod
    def minus(cls, user):
        cls.collection.update(
            {"name": user},
            {"$inc": {"minus": 1}},
            upsert=True
        )

    @classmethod
    def meh(cls, user):
        cls.collection.update(
            {"name": user},
            {"$inc": {"meh": 1}},
            upsert=True
        )

    @classmethod
    def get(cls, user):
        result = cls.collection.find_one({"name": user.title()})
        plus, minus, meh = 0, 0, 0
        if result:
            if result.get('plus'):
                plus = result.get('plus')
            if result.get('minus'):
                minus = result.get('minus')
            if result.get('meh'):
                meh = result.get('meh')

        message = "*Karma* for {0}: {1}++, {2}--, {3}+-".format(
            user,
            plus,
            minus,
            meh
        )
        return message

    @staticmethod
    def top_users():
        return "User List"
