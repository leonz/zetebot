from common import InvalidInputException
from common import needs_zetebot
from common import needs_zetebot_cls
from common import OutputMessage
from config import config


class KnowledgeHandler(object):
    collection = config.db.knowledge


class StoreKnowledgeHandler(KnowledgeHandler):

    @staticmethod
    @needs_zetebot
    def identify(text):
        return text.startswith("know that ")

    @classmethod
    @needs_zetebot_cls
    def handle(cls, input_message):
        # text: x is y OR x are y
        text = input_message.text
        text = ' '.join(text.split(' ')[2:]).strip()

        words = text.split(' are ')
        if len(words) == 1:
            words = text.split(' is ')
        if len(words) == 1:
            raise InvalidInputException()

        x = words[0].lower()

        if x == 'you':
            x = config.botname
            text = text.replace('you are', 'I am')

        cls.collection.update(
            {"x": x},
            {"x": x, "y": text},
            upsert=True
        )

        return OutputMessage(
            channel=input_message.channel,
            text="OK, %s" % text,
        )


class GetKnowledgeHandler(KnowledgeHandler):

    @staticmethod
    @needs_zetebot
    def identify(text):
        has_question_phrase = any(
            text.startswith(phrase) for phrase in
            ('what is ', 'what are ', 'who is', 'who are')
        )

        return has_question_phrase and len(text.split(' ')) > 2

    @classmethod
    @needs_zetebot_cls
    def handle(cls, input_message):
        text = input_message.text.lower()

        x = ' '.join(text.split(' ')[2:]).strip()
        if x == 'you':
            x = config.botname

        result = cls.collection.find_one({"x": x})

        if result is None:
            output_text = "I don't know.  I'm just a useless bot."
        else:
            output_text = result.get('y')

        return OutputMessage(
            channel=input_message.channel,
            text=output_text
        )
