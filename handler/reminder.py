""" This class is only responsible for scheduling events, i.e. storing them
in the database.  A different process polls the database for expiring events """
import datetime

from common import InvalidInputException
from common import needs_zetebot
from common import needs_zetebot_cls
from common import OutputMessage
from config import config
#import time as timemod # Doesn't work as expected on Heroku


GENERAL_CHANNEL = 'C04TKSW4X'
MINIMUM_WAIT_MINS = 5


def from_now(**kwargs):
    return datetime.datetime.now() + datetime.timedelta(**kwargs)


class TimeTooCloseException(Exception):
    """ Raised when a user requests a reminder sooner than MINIMUM_WAIT_MINS """
    pass


class ReminderHandler(object):

    collection = config.db.events

    @staticmethod
    @needs_zetebot
    def identify(text):
        return text.startswith('remind ')

    @classmethod
    @needs_zetebot_cls
    def handle(cls, input_message):
        text = input_message.text

        if text.lower().startswith('remind everyone '):
            channel = GENERAL_CHANNEL
            audience = 'everyone'
            text = text[16:]
        elif text.lower().startswith('remind channel '):
            channel = input_message.channel
            audience = 'this channel'
            text = text[15:]
        else:
            raise InvalidInputException('Bad reminder audience')

        try:
            timestamp, message = text.strip().split(' that ')
        except ValueError:
            raise InvalidInputException('No message in reminder')

        try:
            event_time = cls.get_datetime_from_timestamp(
                timestamp[3:],
                relative=text.lower().startswith('in ')
            )

            if event_time < from_now(minutes=MINIMUM_WAIT_MINS-1):
                raise TimeTooCloseException()

        except TimeTooCloseException:
            print "TimeTooCloseException: %s" % input_message.text
            return OutputMessage(
                channel=input_message.channel,
                text=("Sorry, I can't do that. Give me at least "
                      "5 minutes to schedule a reminder.")
            )

        else:
            cls.collection.insert({
                'time': event_time,
                'user': input_message.user_id,
                'channel': channel,
                'message': message,
                'type': audience if audience is 'everyone' else 'channel',
                'pending': True
            })

            return OutputMessage(
                channel=input_message.channel,
                text="Okay, I'll remind %s then." % audience
            )

    @staticmethod
    def get_datetime_from_timestamp(timestamp, relative=False):
        if not relative:
            date, time = timestamp.split(' at ')
            month, day, year = date.split('/')

            time = time.lower()

            twelve_correction = 0

            if time.endswith('am'):
                time = time[:-2]
                # midnight is 0 in datetime
                if time.startswith('12'):
                    twelve_correction = -12
            elif time.endswith('pm'):
                time = time[:-2]
                twelve_correction = 12

            hour, minute = time.split(':')

            # 4 because we are working off of Eastern time
            tz_offset = 4
            timezone_correction = tz_offset #+ (1 - timemod.localtime().tm_isdst)
            hour_corrected = int(hour) + twelve_correction + timezone_correction

            if hour_corrected > 23:
                hour_corrected -= 24
                day = int(day) + 1

            return datetime.datetime(
                int(year),
                int(month),
                int(day),
                hour_corrected,
                int(minute)
            )

        else:
            amount, unit = timestamp.split(' ')

            if unit.startswith('minute') and int(amount) > 0:
                return from_now(minutes=int(amount))

            elif unit.startswith('hour') and int(amount) > 0:
                return from_now(hours=int(amount))

            else:
                raise InvalidInputException()
