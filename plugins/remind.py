""" This class is only responsible for scheduling events, i.e. storing them
in the database.  A different process polls the database for expiring events """
import datetime
import time as timemod

from config import config
from plugins import InvalidInputException


class ReminderHandler(object):

    collection = config.db.events

    @classmethod
    def schedule(cls, event, channel, user):
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
            elif time.lower().endswith('pm'):
                time = time[:-2]
                pmcorrect = 12

            month, day, year = date.split('/')
            hour, minute = time.split(':')

            event_time = datetime.datetime(
                int(year),
                int(month),
                int(day),
                int(hour) + pmcorrect + 5 - timemod.localtime().tm_isdst, #correct for UTC, AND DAYLIGHsdst = time.localtime().tm_isdstT
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
            'type': 'reminders-everyone',
            'pending': True
        })

        return "Okay, I'll remind everyone then."
