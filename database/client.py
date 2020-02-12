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

    ########################################
    ###########     SESSIONS     ###########
    ########################################

    def insert_session(self, uuid, live=False):
        """ Checks if session exists, otherwise creates it to record its messages """
        session = self.db.sessions.find_one({"uuid": uuid})
        if not session:
            session = {
                "uuid": uuid,
                "live": live,
                "messages": [],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
            return self.db.sessions.insert_one(session)
        return True

    def finish_session(self, uuid):
        """ Checks if session is active and finish it if it is """
        session = self.db.sessions.find_one({"uuid": uuid})
        if session and "finishedAt" not in session:
            return self.db.sessions.update_one({"_id": session["_id"]}, {"$set": {"finishedAt": datetime.now()}})
        return False

    def get_sessions(self, filters={}):
        """ Fetches sessions from database, applying given filters """
        return self.db.sessions.find(filters)

    def insert_message(self, uuid, text, response, df_intent):
        """ Inserts new message, and generated reponse and triggered Dialogflow intent, for a given session """
        data = {
            "text": text,
            "response": response,
            "dfIntent": df_intent,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        return self.db.sessions.update_one({"uuid": uuid}, {"$push": {"messages": data}, "$set": {"updatedAt": datetime.now()}})

    #######################################
    ###########     INTENTS     ###########
    #######################################

    def get_latest_intent(self, uuid):
        return self.db.intents.find_one({"session": uuid}, sort=[("createdAt", pymongo.DESCENDING)])

    def update_intent(self, id, new_values):
        new_values['updatedAt'] = datetime.now()
        return self.db.intents.update_one({"_id": id}, {"$set": new_values})

    def insert_intent(self, uuid, text, entities, nile):
        data = {
            "session": uuid,
            "text": text,
            "entities": entities,
            "nile": nile,
            "status": "pending",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        return self.db.intents.insert_one(data)

    def get_intents(self, uuid):
        return self.db.intents.find({"session": uuid})

    def get_confirmed_intents(self, uuid):
        return self.db.intents.find({"session": uuid, "status": {"$ne": "pending"}})

    #########################################
    ###########     CONFLICTS     ###########
    #########################################

    def insert_conflict(self, uuid, old_intent, new_intent, features, result):
        data = {
            "session": uuid,
            "old_intent": old_intent,
            "new_intent": new_intent,
            "result": result,
            "features": features,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        return self.db.conflicts.insert_one(data)
