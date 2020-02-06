""" Conflicts check module """

from conflicts.features import get_features
from conflicts.model import ClassificationModel

from database import client


def check(new_intent, session):
    """ Checks new intent for conflicts """
    model = ClassificationModel('forest')
    contradictory = None
    if model.load(10000):
        db = client.Database()
        confirmed_intents = db.get_confirmed_intents(session)
        for intent in confirmed_intents:
            if intent['_id'] != new_intent['_id']:
                features = get_features(new_intent['nile'], intent['nile'])
                print("Extracted features:", features)
                res = model.predict([features])
                print('Conflict?', res)
                db.insert_conflict(session, intent, new_intent, features, bool(res[0]))
                if res[0]:
                    print("conflict detected!")
                    contradictory = intent
                    break
    else:
        print("Failure loading conflict model. Will continue without it.")

    return contradictory


if __name__ == '__main__':
    test_intent = {
        "session": "61267680-3312-11ea-b930-4d253fcf2f04",
        "nile": "define intent uniIntent: remove middlebox('firewall') for endpoint('network')"
    }
    check(test_intent, test_intent['session'])
