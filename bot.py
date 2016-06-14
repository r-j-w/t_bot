import bot_lib
import sys
import boto3
import signal
import time
from bot_parser import bot_parser_thread

BOT_CONFIG = bot_lib.parse_config() or sys.exit(1)

# Get top streams
twitch_api = bot_lib.twitch_api()

# Merge channel list from api with configured list
channel_list = twitch_api.get_top_stream_list() | BOT_CONFIG['irc']['channel_list']

# channel_list = ['forsenlol']

print "Connecting to: {}".format(','.join(channel_list))

irc = bot_lib.twitch_irc()
irc.connect(username=BOT_CONFIG['irc']['username'], password=BOT_CONFIG['irc']['password'])

irc.join_channels(channel_list)


def sig_handler(signal, frame):
    print 'SIGNAL {} RECEIVED. CLOSING IRC SOCKET'.format(signal)
    irc.disconnect()
    sys.exit()

for s in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(s, sig_handler)

message_cache = {c: [] for c in channel_list}

time_span_begin = time.time()

while True:
    irc_msg = irc.receive()

    # If pinged, then pong back
    if irc_msg.startswith('PING :tmi.twitch.tv'):
        irc.send('PONG :tmi.twitch.tv\r\n')

    msg = bot_lib.twitch_message(irc_msg)

    if msg.user_name and msg.message:
        try:
            #print "{}|{}: {}".format(msg.channel, msg.user_name, msg.message)
            message_cache[msg.channel].append(msg.message)
        except UnicodeEncodeError:
            pass

    # If 5 seconds have lapsed then spawn thread to write to db
    if time.time() - time_span_begin >= 5:
        print("5 seconds have passed!")

        bot_parser_thread(
            dynamo_table=BOT_CONFIG['dynamo']['emote_count_table'],
            messages=message_cache,
            time_frame=(time.time() - time_span_begin)
        ).start()
    
        message_cache = {c: [] for c in channel_list}

        # Reset time span
        time_span_begin = time.time()
