import threading
import re
import time
import boto3


class bot_parser_thread(threading.Thread):
    def __init__(self, dynamo_table, messages, emote_dict={}, time_frame=5):
        self.start_time = time.time()
        threading.Thread.__init__(self)
        self.dynamo_table = dynamo_table
        self.messages = messages
        self.emote_dict = emote_dict
        self.time_frame = int(time_frame)

    def run(self):
        # Connect to dynamo & open table
        #dynamo = boto3.resource('dynamodb').Table(self.dynamo_table)

        self.emote_counts = {}

        for channel in self.messages:
            self.emote_counts.setdefault(channel, {})

            # Check for emotes in messages
            for e in self.emote_dict:
                self.emote_counts[channel][e] = len([x for x in self.messages[channel] if self.emote_dict[e].search(x)])

        self.test_print()

        print "Exec time: {:.5f}".format(time.time() - self.start_time)

    def test_print(self):
        """
        Just to test printing the results
        """
        for channel in self.emote_counts:
            print "{:20s}: {:3d} {:3d}/m Kappas: {} gachiGASMs: {} WutFaces: {} SourPls: {} LULs: {}".format(
                channel,
                len(self.messages[channel]),
                len(self.messages[channel]) * (60 / self.time_frame),
                self.emote_counts[channel]['Kappa'],
                self.emote_counts[channel]['gachiGASM'],
                self.emote_counts[channel]['WutFace'],
                self.emote_counts[channel]['SourPls'],
                self.emote_counts[channel]['LUL'],
            )