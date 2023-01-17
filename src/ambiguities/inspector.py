""" Ambiguities check module """

from .features import get_features
from .model import ClassificationModel

from ..database import client

TRAINED_MODEL_SIZE = 10000


def check(new_intent, session):
    """Checks new intent for ambiguities"""
    model = ClassificationModel("forest")
    contradictory = None
    if model.load(TRAINED_MODEL_SIZE):
        db = client.Database()
        confirmed_intents = db.get_confirmed_intents(session)
        print("intent", confirmed_intents)
        for intent in confirmed_intents:
            print("intent", intent)
            if intent["_id"] != new_intent["_id"]:
                features = get_features(new_intent["nile"], intent["nile"])
                print("Extracted features:", features)
                res = model.predict([features])
                print("Ambiguity?", res)
                db.insert_amibiguity(
                    session, intent, new_intent, features, bool(res[0])
                )
                if res[0]:
                    print("Ambiguity detected!")
                    contradictory = intent
                    break
    else:
        print("Failure loading ambiguity model. Will continue without it.")

    return contradictory


if __name__ == "__main__":
    test_intent = {
        "_id": "test_intent",
        "session": "c2776a80-3d52-11ea-89dc-8bf5fe8b3de0",
        "nile": "define intent stnIntent: for group('dorms') add middlebox('ips')",
    }
    check(test_intent, test_intent["session"])
