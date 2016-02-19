from collections import namedtuple
from functools import wraps

from config import config

InputMessage = namedtuple('InputMessage', ['user_id', 'channel', 'text'])
OutputMessage = namedtuple('OutputMessage', ['channel', 'text'])


class InvalidInputException(Exception):
    """ Called when a zetebot command is written with invalid syntax.
        Ideally be aware of these to make zetebot more intuitive. """
    pass


class NoResponseException(Exception):
    """ Called when a zetebot command expects no response. """
    pass


class NotZetebotActivityException(Exception):
    """ The activity received is from zetebot.  Ignore it. """
    pass


def needs_zetebot(func):
    """ A decorator to be used for all handlers that require
        'zetebot' at the start the message text to be invoked.
    """
    @wraps(func)
    def _func_decorated(arg):
        return func(_strip_zetebot(arg))
    return _func_decorated


def needs_zetebot_cls(func):
    """ Same as above, for class methods. """
    def _func_decorated(cls, arg):
        return func(cls, _strip_zetebot(arg))
    return _func_decorated


def _strip_zetebot(message):
    """ message is a string, unicode, or InputMessage """
    start_len = len(config.botname) + 1
    print message
    if type(message) in (str, unicode):
        if not message[:start_len].lower() == config.botname + ' ':
            return ''
        return message[start_len:]
    else:
        result_text = ''
        if message.text[:start_len].lower() == config.botname + ' ':
            result_text = message.text[start_len:]

        return InputMessage(
            user_id=message.user_id,
            channel=message.channel,
            text=result_text
        )
