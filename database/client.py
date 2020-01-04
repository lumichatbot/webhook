import redis
import configparser


class Database:
    """ Class to encapsule database operations, such as storing intents and feedback information """

    client = None

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('/etc/lumi/config.ini')
        self.client = redis.Redis(
            host=config['DATABASE']['hostname'],
            port=config['DATABASE']['port'],
            password=config['DATABASE']['password'])

    def record_intent(self, intent):
        self.client.lpush('Intents', intent)
        return True
