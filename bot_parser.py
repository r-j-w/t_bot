import bot_lib
import sys
import time
import re
import redis
import threading

BOT_CONFIG = bot_lib.parse_config() or sys.exit(1)


class bot_parser_thread(threading.Thread):
    def __init__(self, channel):
        threading.Thread.__init__(self)
        self.channel = channel

    def run(self):
        # Setup redis connection
        self._redis = redis.StrictRedis(host=BOT_CONFIG['redis']['endpoint'])
        # Subscribe to channel
        self._redis_pubsub = self._redis.pubsub()
        self._redis_pubsub.subscribe(self.channel)

        print 'Thread started {} for channel {}'.format(threading.current_thread().name, self.channel)

        # Listen to the redis channel and print any messages
        while True:
            for m in self._redis_pubsub.listen():
                print "{}: {}".format(self.channel, m.get('data'))

# Get channels to listen on (redis channels) as a list to later support multiple channels
channels_to_monitor = [c.strip('#') for c in BOT_CONFIG['connection']['channels'].split(',')]

for chan in channels_to_monitor:
    print 'Starting parser for ' + chan
    bot_parser_thread(chan).start()

print 'Exiting main thread'

# dynamodb = boto3.resource('dynamodb')
# dynamo_table = dynamodb.Table('twitch_messages')
