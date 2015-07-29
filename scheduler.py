#!/usr/bin/env python
""" This is a scheduler that polls the MongoDB looking for new events.

It's run separately as a CRON job."""
import datetime
import os

import requests
from pymongo import MongoClient


class ZetebotScheduler(object):

    collection = MongoClient(os.environ['DB_URI']).heroku_87j7x208.events

    def send(self, channel, message):
        requests.post(
            'https://slack.com/api/chat.postMessage?token=%s&channel=%s&text=%s&username=%s&as_user=%s'
            % (os.environ['SLACK_AUTH'], channel, message, 'zetebot', 'True')
        )

    def run(self):
        try:
            now = datetime.datetime.utcnow()
            event = self.collection.find_one_and_update(
                {
                    'time': {'$lt': now},
                    'pending': True
                },
                {
                    '$set': {'pending': False}
                }
            )

            if not event:
                print "No events found"
            else:
                print "Found an event. Posting: %s" % event.get('message')
                channel = event.get('channel')
                message = '*Reminder for @everyone:* ' + event.get('message')
                self.send(channel, message)

        except Exception as e:
            result = "Scheduler Exception: %s" % repr(e)
            self.send(os.environ['DEBUG_CHANNEL'], result)

if __name__ == '__main__':
    ZetebotScheduler().run()
