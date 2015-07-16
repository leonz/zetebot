from config import config
from plugins import InvalidInputException


class KarmaHandler(object):

    def __init__(self, user):
        self.user = user.title()
        self.collection = config.db.karma

    def handle(self, text):
        if '++' in text:
            self.user = self.grab_user_from_text(text, '++')
            self.plus()
        elif '--' in text:
            self.user = self.grab_user_from_text(text, '--')
            self.minus()
        elif '+-' in text:
            self.user = self.grab_user_from_text(text, '+-')
            self.meh()
        else:
            raise InvalidInputException()

    @staticmethod
    def grab_user_from_text(text, changer):
        return [x for x in text.split(' ') if
                x.endswith(changer)][0][:-2].title()

    def plus(self):
        self.collection.update(
            {"name": self.user},
            {"$inc": {"plus": 1}},
            upsert=True
        )

    def minus(self):
        self.collection.update(
            {"name": self.user},
            {"$inc": {"minus": 1}},
            upsert=True
        )

    def meh(self):
        self.collection.update(
            {"name": self.user},
            {"$inc": {"meh": 1}},
            upsert=True
        )

    def get(self):
        result = self.collection.find_one({"name": self.user})
        plus, minus, meh = 0, 0, 0
        if result:
            if result.get('plus'):
                plus = result.get('plus')
            if result.get('minus'):
                minus = result.get('minus')
            if result.get('meh'):
                meh = result.get('meh')

        message = "*Karma* for {0}: {1}++, {2}--, {3}+-".format(
            self.user,
            plus,
            minus,
            meh
        )
        return message

    @staticmethod
    def top_users():
        return "User List"
