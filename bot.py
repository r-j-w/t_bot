import bot_lib
import socket
import sys
import boto3
import redis
import ssl
import signal

BOT_CFG = bot_lib.parse_config() or sys.exit(1)

# Setup redis connection
_redis = redis.StrictRedis(host=BOT_CFG['redis']['endpoint'])

dynamodb = boto3.resource('dynamodb')
dynamo_table = dynamodb.Table('twitch_messages')

# Get top streams
twitch = bot_lib.twitch_api()

# Merge channel list from api with configured list
channel_list = twitch.get_top_stream_list() | BOT_CFG['connection']['channel_list']

print "Connecting to: {}".format(','.join(channel_list))

irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc = ssl.wrap_socket(irc_socket)
irc.connect((BOT_CFG['connection']['server'], BOT_CFG['connection']['port']))


irc.send("PASS {}\n".format(BOT_CFG['connection']['password']))
irc.send("USER {} {} {} :hi\n".format(BOT_CFG['connection']['botnick'], BOT_CFG['connection']['botnick'], BOT_CFG['connection']['botnick']))
irc.send("NICK {}\n".format(BOT_CFG['connection']['botnick']))
irc.send("PRIVMSG nickserv :identify {} {}\r\n".format(BOT_CFG['connection']['botnick'], BOT_CFG['connection']['password']))
irc.send("JOIN #{}\n".format(',#'.join(channel_list)))


def sig_int_handler(signal, frame):
    print 'SIGINT RECEIVED. CLOSING IRC SOCKET'
    irc_socket.shutdown(socket.SHUT_RDWR)
    irc_socket.close()
    sys.exit()

signal.signal(signal.SIGINT, sig_int_handler)

while True:
    irc_msg = irc.recv(2040).decode('utf-8')

    # If pinged, then pong back
    if irc_msg.startswith('PING :tmi.twitch.tv'):
        irc.send('PONG :tmi.twitch.tv\r\n'.encode())

    msg = bot_lib.twitch_message(irc_msg)

    if msg.user_name and msg.message:
        try:
            print "{}|{}: {}".format(msg.channel, msg.user_name, msg.message)
            _redis.publish(msg.channel, msg.message)
        except UnicodeEncodeError:
            pass
