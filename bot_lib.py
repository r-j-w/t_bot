import ConfigParser
import re
import time
import logging
import requests


TWITCH_MSG_REGEX = re.compile(r'^:(?P<user>.+)!.+@.*.tmi.twitch.tv\sPRIVMSG\s#(?P<channel>.+)\s:(?P<msg>.+)', flags=re.M)


def __log__(msg):
    logging.info(msg)


def parse_config(config_file='twitch_irc.cfg'):
    c_parser = ConfigParser.ConfigParser()
    c_parser.read(config_file)
    cfg = {}

    for cfg_key in c_parser.sections():
        cfg.setdefault(cfg_key, {})
        for cfg_item in c_parser.items(cfg_key):
            cfg[cfg_key].update({cfg_item[0]: cfg_item[1]})

    for x in ['server', 'botnick', 'password', 'channels']:
        if x not in cfg['connection']:
            print "Missing config option: {}".format(x)
            return

    cfg['connection']['port'] = int(cfg['connection']['port'])
    cfg['connection']['channel_list'] = set([x for x in cfg['connection']['channels'].split(',') if x])

    return cfg


class twitch_api():
    ENDPOINT = 'https://api.twitch.tv/kraken/'
    HEADERS = {'Accept': 'application/vnd.twitchtv.v3+json'}

    def __init__(self):
        pass

    def __get(self, url, url_params=None):
        return requests.get(
            self.ENDPOINT + url,
            params=url_params,
            headers=self.HEADERS).json()

    def get_top_stream_list(self, limit=25):
        url_params = {'limit': limit}
        streams = self.__get('streams', url_params=url_params)['streams']
        streams = [s['channel']['name'] for s in streams]
        return set(streams)


class twitch_message():
    def __init__(self, msg):
        self.text = msg.strip()
        self.user_name, self.message, self.channel, self.timestamp = None, None, None, int(time.time())

        match = TWITCH_MSG_REGEX.match(self.text)

        if match:
            self.user_name = match.group('user').strip()
            self.channel = match.group('channel').strip()
            self.message = match.group('msg').strip()
            # self.store_message()
            # self.publish_message()

    def store_message(self):
        # dynamo_table.put_item(Item={
        #     'user': self.user_name,
        #     'channel': self.channel,
        #     'message': self.message,
        #     'timestamp': self.timestamp
        # })
        pass

    def publish_message(self):
        # _redis.publish(self.channel, self.message)
        pass
