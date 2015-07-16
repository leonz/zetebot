from config import config


class KnowledgeHandler(object):

    collection = config.db.knowledge

    @classmethod
    def learn(cls, text):
        """ text: x is y OR x are y """
        words = text.split(' are ')
        if len(words) == 1:
            words = text.split(' is ')
        x = words[0].lower()

        if x == 'you':
            x = config.botname
            text = text.replace('you are', 'I am')

        if words[1].lower() not in ('is', 'are'):
            return

        cls.collection.update(
            {"x": x},
            {"x": x, "y": text},
            upsert=True
        )

        return "OK, %s" % text

    @classmethod
    def retrieve(cls, question):
        """ text: x is y OR x are y """
        result = cls.collection.find_one({"x": question})
        if result is None:
            return "I don't know.  I'm just a useless bot."

        if result == 'you':
            return "I'm the soul of John Harvey."

        return result.get('y')
