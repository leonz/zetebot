import pymongo
from pymongo import MongoClient
import os

class Database:
    client = MongoClient(os.environ['DB_URI'])
    db = client.heroku_87j7x208
