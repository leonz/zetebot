""" This class is only responsible for scheduling events, i.e. storing them
in the database.  A different process polls the database for expiring events """
import datetime
import time as timemod

from config import config
from plugins import InvalidInputException


class ReminderHandler(object):

    collection = config.db.events

    @classmethod
    def schedule(cls, event, channel, user, type_):
        timestamp, message = event.split(' that ')
        message = message.strip()
        if not message:
            raise InvalidInputException('No message in reminder')

        timestamp = timestamp[3:]
        if event.startswith('on '):
            date, time = timestamp.split(' at ')

            pmcorrect = 0

            if time.lower().endswith('am'):
                time = time[:-2]
                if time.startswith('12'):
                    pmcorrect = -12
            elif time.lower().endswith('pm'):
                time = time[:-2]
                pmcorrect = 12

            month, day, year = date.split('/')
            hour, minute = time.split(':')

            # 4 because we are working off of Eastern time
            timezone_correction = 4 + (1 - timemod.localtime().tm_isdst)
            hour_corrected = int(hour) + pmcorrect + timezone_correction

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

            if event_time < datetime.datetime.utcnow() + datetime.timedelta(minutes=5):
                return "Sorry, can't do that. Give at least 5 minutes to schedule a reminder."

        elif event.startswith('in '):
            amount, unit = timestamp.split(' ')
            if unit.startswith('minute'):
                if int(amount) < 5:
                    return "Sorry, can't do that. Give at least 5 minutes to schedule a reminder."

                event_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=int(amount))

            elif unit.startswith('hour'):
                if int(amount) < 1:
                    raise InvalidInputException('Invalid amount for hours to reminder')

                event_time = datetime.datetime.utcnow() + datetime.timedelta(hours=int(amount))

        cls.collection.insert({
            'time': event_time,
            'user': user,
            'channel': channel,
            'message': message,
            'type': type_,
            'pending': True
        })

        if type_ == 'channel':
            them = 'the channel'
        else:
            them = 'everyone'

        return "Okay, I'll remind %s then." % them
