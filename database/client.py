import pymongo
import os

from datetime import datetime


class Database:
    """ Class to encapsule database operations, such as storing intents and feedback information """

    db = None

    def __init__(self):
        db_user = os.getenv("DB_USERNAME")
        db_pass = os.getenv("DB_PASSWORD")

        client = pymongo.MongoClient(
            "mongodb+srv://{}:{}@lumichatbot-nawdk.mongodb.net/lumi?retryWrites=true&w=majority"
            .format(db_user, db_pass))
        self.db = client.lumi

    def insert_session(self, uuid):
        """ Checks if session exists, otherwise creates it to record its messages """
        session = self.db.session.find_one({'uuid': uuid})
        if not session:
            session = {
                "uuid": uuid,
                "createdAt": datetime.now(),
                "messages": []
            }
            return self.db.session.insert_one(session)
        return True

    def insert_message(self, uuid, text, response, df_intent):
        """ Inserts new message, and generated reponse and triggered Dialogflow intent, for a given session """
        data = {
            "createdAt": datetime.now(),
            "text": text,
            "response": response,
            "dfIntent": df_intent
        }
        return self.db.session.update_one({"uuid": uuid}, {'$push': {'messages': data}})

    def insert_intent(self, uuid, intent, entities, nile):
        data = {
            'uuid': uuid,
            'intent': intent,
            'entities': entities,
            'nile': nile
        }
        return self.db.intents.insert_one(data)

    def insert_confirmed_intent(self, uuid, intent, entities, nile):
        data = {
            'uuid': uuid,
            'intent': intent,
            'entities': entities,
            'nile': nile
        }
        return self.db.confirmed_intents.insert_one(data)
