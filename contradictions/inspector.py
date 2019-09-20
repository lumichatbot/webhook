""" Contradictions check module """

from contradictions.features import get_features
from contradictions.model import ClassificationModel
from utils import storage


def check(new_intent):
    """ Checks new intent for contradictions """
    model = ClassificationModel('forest')
    contradictory = None
    if model.load_model(10000):
        for old_intent in storage.get_all():
            res = model.predict([get_features(new_intent, old_intent)])
            print res
            if res:
                contradictory = old_intent
                break
    else:
        print "Failure loading contradiction model. Will continue without it."

    return contradictory


if __name__ == '__main__':
    test_intent = "define intent uniIntent: from endpoint('19.16.1.1') to service('netflix') add middlebox('loadbalancer'), middlebox('firewall') start hour('10:00') end hour('10:00')"
    check(test_intent)
