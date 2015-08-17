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
        post_url = (
            'https://slack.com/api/chat.postMessage?'
            'token={0}&channel={1}&text={2}&username={3}&as_user={4}'
        ).format(
            os.environ['SLACK_AUTH'],
            channel,
            message,
            'zetebot',
            'True'
        )
        requests.post(post_url)

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
                print 'Found an event. Posting: %s' % event.get('message')
                channel = event.get('channel')
                message = '*Reminder for <!%s>:* %s' % (
                    event.get('type'),
                    event.get('message')
                )
                self.send(channel, message)

        except FinishedException:
            # Break out of the loop, we found nothing new
            print 'No events found'
            raise

        except Exception as e:
            result = 'Scheduler Exception: %s' % repr(e)
            self.send(os.environ['DEBUG_CHANNEL'], result)

if __name__ == '__main__':
    while True:
        ZetebotScheduler().run()
