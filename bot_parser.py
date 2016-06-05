import threading
import re
import time
import boto3


class bot_parser_thread(threading.Thread):
    emotes = ['Kappa', 'LUL', 'gachiGASM', 'SMOrc', 'FeelsBadMan', '4Head', 'haHAA' ]

    def __init__(self, dynamo_table, channel, messages, time_frame=5):
        self.start_time = time.time()
        threading.Thread.__init__(self)
        self.dynamo_table = dynamo_table
        self.channel = channel
        self.messages = messages
        self.time_frame = int(time_frame)

    def run(self):
        # Connect to dynamo & open table
        #dynamo = boto3.resource('dynamodb').Table(self.dynamo_table)

        self.emote_counts = {e: 0 for e in self.emotes}

        # Check for emotes in messages
        for e in self.emotes:
            r = re.compile(r'(?:^' + e + '\s|\s' + e + '\s|' + e + '$)')
            self.emote_counts[e] = len([x for x in self.messages if r.search(x)])

        print "{:20s}: {:3d} {:3d}/m Kappas: {} LULs: {} Exec time: {:.5f}".format(
            self.channel,
            len(self.messages),
            len(self.messages) * (60 / self.time_frame),
            self.emote_counts['Kappa'],
            self.emote_counts['LUL'],
            time.time() - self.start_time,
        )
