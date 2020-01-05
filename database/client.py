import pymongo
import os


class Database:
    """ Class to encapsule database operations, such as storing intents and feedback information """

    db = None

    def __init__(self):
        db_user = os.getenv("DB_USERNAME")
        db_pass = os.getenv("DB_PASSWORD")

        client = pymongo.MongoClient(
            "mongodb+srv://{}:{}@lumichatbot-nawdk.mongodb.net/test?retryWrites=true&w=majority"
            .format(db_user, db_pass))
        self.db = client.test

    def insert_intent(self, uuid, intent, entities, nile):
        data = {
            'uuid': uuid,
            'intent': intent,
            'entities': entities,
            'nile': nile
        }
        self.db.intents.insert_one(data)
        return True
