#!/usr/bin/env python
""" This is a scheduler that polls the MongoDB looking for new events.
It's run on a separate process from Zetebot

Currently, I have Zetebot running on Heroku while the scheduler runs
on Openshift """
import datetime
import os

import requests
from pymongo import MongoClient

class FinishedException(Exception):
    pass

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
                raise FinishedException()
            else:
                print "Found an event. Posting: %s" % event.get('message')
                channel = event.get('channel')
                message = '*Notice for <!%s>:* %s' % (event.get('type'), event.get('message'))
                self.send(channel, message)
        except FinishedException as e:
            # Break out of the loop, we found nothing new
            print "No events found"
            raise e
        except Exception as e:
            result = "Scheduler Exception: %s" % repr(e)
            self.send(os.environ['DEBUG_CHANNEL'], result)

if __name__ == '__main__':
    while True:
        ZetebotScheduler().run()
