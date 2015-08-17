import os

from pymongo import MongoClient


class config:
    botname = 'zetebot'
    botid = 'U07LBDK89'
    db = MongoClient(os.environ['DB_URI']).heroku_87j7x208
    slack_token = os.environ['SLACK_AUTH']
    debug = os.environ['DEBUG_CHANNEL']
