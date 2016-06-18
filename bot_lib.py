import ConfigParser
import re
import time
import logging
import requests
import socket
import ssl


TWITCH_MSG_REGEX = re.compile(r'^:(?P<user>.+)!.+@.*.tmi.twitch.tv\sPRIVMSG\s#(?P<channel>[\w]+)\s:(?P<msg>.+)', flags=re.M)


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

    for x in ['username', 'password', 'channels']:
        if x not in cfg['irc']:
            print "Missing config option: {}".format(x)
            return

    cfg['irc']['channel_list'] = set([x for x in cfg['irc']['channels'].split(',') if x])
    cfg['emotes']['emote_dict'] = {e: re.compile(r'(?:^' + e + '\s|\s' + e + '\s|' + e + '$)') for e in cfg['emotes']['emote_list'].split(',')}

    return cfg


class twitch_irc():
    def __init__(self):
        self.irc_server = 'irc.chat.twitch.tv'
        self.irc_port = 443

    def connect(self, username, password):
        # Open socket connection to twitch irc
        self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc = ssl.wrap_socket(self.irc_socket)
        self.irc.connect((self.irc_server, self.irc_port))

        # Authenticate
        self.irc.send("PASS {}\r\n".format(password))
        self.irc.send("USER {} {} {} :hi\r\n".format(username, username, username))
        self.irc.send("NICK {}\r\n".format(username))

    def join_channels(self, channels):
        if isinstance(channels, str):
            channels = [channels]
        self.irc.send("JOIN #{}\r\n".format(',#'.join(channels)))

    def send(self, message):
        self.irc.send(message.encode())

    def receive(self):
        return self.irc.recv(2040).decode('utf-8')

    def disconnect(self):

        self.irc_socket.shutdown(socket.SHUT_RDWR)
        self.irc_socket.close()


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
