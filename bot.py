import bot_lib
import socket
import sys
import boto3
import redis

BOT_CFG = bot_lib.parse_config() or sys.exit(1)

# Setup redis connection
_redis = redis.StrictRedis(host=BOT_CFG['redis']['endpoint'])

dynamodb = boto3.resource('dynamodb')
dynamo_table = dynamodb.Table('twitch_messages')

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((BOT_CFG['connection']['server'], 6667))

irc.send("PASS {}\n".format(BOT_CFG['connection']['password']))
irc.send("USER {} {} {} :hi\n".format(BOT_CFG['connection']['botnick'], BOT_CFG['connection']['botnick'], BOT_CFG['connection']['botnick']))
irc.send("NICK {}\n".format(BOT_CFG['connection']['botnick']))
irc.send("PRIVMSG nickserv :identify {} {}\r\n".format(BOT_CFG['connection']['botnick'], BOT_CFG['connection']['password']))
irc.send("JOIN {}\n".format(BOT_CFG['connection']['channels']))

while True:
    msg = bot_lib.twitch_message(irc.recv(2040))

    if msg.user_name and msg.message:
        try:
            print "{}: {}".format(msg.user_name, msg.message)
            _redis.publish(msg.channel, msg.message)
        except UnicodeEncodeError:
            pass
