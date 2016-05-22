import socket
import sys
import time
import logging
import re
import boto3
import ConfigParser

c_parser = ConfigParser.ConfigParser()
c_parser.read('twitch_irc.cfg')
cfg = {}

for cfg_item in c_parser.items('connection'):
    cfg.update({cfg_item[0]: cfg_item[1]})

for x in ['server', 'botnick', 'password', 'channel']:
    if x not in cfg:
        print "Missing config option: {}".format(x)
        sys.exit(1)

twitch_msg_regex = re.compile(r'^:(?P<user>.+)!.+@.*.tmi.twitch.tv\sPRIVMSG\s#(?P<channel>.+)\s:(?P<msg>.+)', flags=re.M)

dynamodb = boto3.resource('dynamodb')
dynamo_table = dynamodb.Table('twitch_messages')

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((cfg['server'], 6667))

irc.send("PASS {}\n".format(cfg['password']))
irc.send("USER {} {} {} :hi\n".format(cfg['botnick'], cfg['botnick'], cfg['botnick']))
irc.send("NICK {}\n".format(cfg['botnick']))
irc.send("PRIVMSG nickserv :identify {} {}\r\n".format(cfg['botnick'], cfg['password']))
irc.send("JOIN {}\n".format(cfg['channel']))

class twitch_message():
    def __init__(self, msg):
        self.text = msg.decode('utf-8')
        self.user_name, self.message, self.channel, self.timestamp = None, None, None, int(time.time())

        match = twitch_msg_regex.match(self.text)
        
        if match:
           self.user_name = match.group('user')
           self.channel = match.group('channel')
           self.message = match.group('msg')
           self.store_message()

    def store_message(self):
        dynamo_table.put_item(Item={
            'user': self.user_name,
            'channel': self.channel,
            'message': self.message,
            'timestamp': self.timestamp
        })


while True:
    msg = twitch_message(irc.recv(2040))

    if msg.user_name:
        try:
            print "{}: {}".format(msg.user_name, msg.message)
        except UnicodeEncodeError:
            pass
