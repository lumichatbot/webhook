""" Intent storage """


STORAGE = []


def add(intent):
    """ Includes new intent in intent storage """
    STORAGE.append(intent)


def get_all():
    """ Returns list of deployed intent """
    return STORAGE
