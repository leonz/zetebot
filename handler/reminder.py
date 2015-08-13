""" This class is only responsible for scheduling events, i.e. storing them
in the database.  A different process polls the database for expiring events """
import datetime
import time as timemod

from common import InvalidInputException
from common import needs_zetebot
from config import config


def from_now(**kwargs):
    return datetime.datetime.now() + datetime.timedelta(**kwargs)


class ReminderHandler(object):

    collection = config.db.events

    @staticmethod
    @needs_zetebot
    def identify(text):
        return text.startswith('remind ')


    @classmethod
    def schedule(cls, event, channel, user, type_):
        timestamp, message = event.split(' that ')
        message = message.strip()
        if not message:
            raise InvalidInputException('No message in reminder')

        timestamp = timestamp[3:]
        if event.startswith('on '):
            date, time = timestamp.split(' at ')
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

            month, day, year = date.split('/')
            hour, minute = time.split(':')

            # 4 because we are working off of Eastern time
            tz_offset = 4
            timezone_correction = tz_offset + (1 - timemod.localtime().tm_isdst)
            hour_corrected = int(hour) + twelve_correction + timezone_correction

            if hour_corrected > 23:
                hour_corrected -= 24
                day = int(day) + 1

            event_time = datetime.datetime(
                int(year),
                int(month),
                int(day),
                hour_corrected,
                int(minute)
            )

            if event_time < from_now(minutes=5):
                return ("Sorry, can't do that. Give at least 5 minutes "
                        "to schedule a reminder.")

        elif event.startswith('in '):

            amount, unit = timestamp.split(' ')

            if unit.startswith('minute'):
                if int(amount) < 5:
                    return ("Sorry, can't do that. Give at least 5 minutes "
                            "to schedule a reminder.")
                else:
                    event_time = from_now(minutes=int(amount))
            elif unit.startswith('hour'):
                if int(amount) < 1:
                    raise InvalidInputException(
                        'Invalid amount for hours to reminder'
                    )
                else:
                    event_time = from_now(hours=int(amount))

        cls.collection.insert({
            'time': event_time,
            'user': user,
            'channel': channel,
            'message': message,
            'type': type_,
            'pending': True
        })

        them = 'the channel' if type_ == 'channel' else 'everyone'
        return "Okay, I'll remind %s then." % them
