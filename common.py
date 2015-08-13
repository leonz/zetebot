from collections import namedtuple

InputMessage = namedtuple('InputMessage', ['user_id', 'channel', 'text'])
OutputMessage = namedtuple('OutputMessage', ['channel', 'text'])


class InvalidInputException(Exception):
    """ Called when a zetebot command is written with invalid syntax.
        Ideally be aware of these to make zetebot more intuitive. """
    pass


class NoResponseException(Exception):
    """ Called when a zetebot command expects no response. """
    pass

from functools import wraps

def needs_zetebot(func):
    """ A decorator to be used for all handlers that require
        'zetebot' at the start the message text to be invoked.
    """
    @wraps(func)
    def _func_decorated(arg):
        return func(_strip_zetebot(arg))
    return _func_decorated


def needs_zetebot_cls(func):
    """ Same as above, for class methods. Temporary
        until I figure out a way to use the above better.
    """
    def _func_decorated(cls, arg):
        return func(cls, _strip_zetebot(arg))
    return _func_decorated


def _strip_zetebot(message):
    """ message is a string, unicode, or InputMessage """
    if type(message) in (str, unicode):
        return message[8:]
    else:
        return InputMessage(
            user_id=message.user_id,
            channel=message.channel,
            text=message.text[8:]
        )
