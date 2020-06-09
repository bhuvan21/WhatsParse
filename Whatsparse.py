import re
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import numpy as np

class WhatsParse:

    def __init__(self, filename):
        self.filename = filename
        self.megx = re.compile('\[(\d{2})\/(\d{2})\/(\d{4}), (\d{2}):(\d{2}):(\d{2})\] ([\w\-\"\s]+): (.*)')
        self.extrx = re.compile("\[(\d{2})\/(\d{2})\/(\d{4}), (\d{2}):(\d{2}):(\d{2})\] (.*)")
        with open(filename, "r", encoding='utf8') as f:
            self.text = f.read()
        self.lines = self.text.split("\n")
        self.msgs = []
        self.senders = []

        for line in self.lines[1:]:
            match = self.megx.match(line)
            if match is not None:
                self.msgs.append({"sender":match.group(7), "body":match.group(8), "date":datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)), int(match.group(4)), int(match.group(5)), int(match.group(6)) )} )
                if match.group(7) not in self.senders:
                    self.senders.append(match.group(7))
            elif self.extrx.match(line):
                pass
            else:
                last_msg = self.msgs[-1]
                self.msgs[-1] = {"sender":last_msg["sender"], "body":last_msg["body"]+ "\n" + line, "date": last_msg["date"]}

    def graph_over_time(self, filterf):

        traces = [[[], []] for x in self.senders]
        startdate = self.msgs[0]["date"].date()
        dates = []
        index = 0

        for msg in self.msgs:
            if msg["date"].day != startdate:
                startdate = msg["date"].date()
            
            if startdate not in dates:
                dates.append(startdate)
                index += 1
                for trace in traces:
                    trace[0].append(matplotlib.dates.date2num(datetime.combine(startdate, datetime.min.time())))
                    trace[1].append(0)

            count = filterf(msg)
            traces[self.senders.index(msg["sender"])][1][-1] += count
            
        for trace in traces:
            plt.plot_date(trace[0], trace[1], "-")
            
        for trace in traces:
            z = np.polyfit(trace[0], trace[1], 1)
            p = np.poly1d(z)
            plt.plot(trace[0],p(trace[0]), linewidth=3)
        
        formatter = matplotlib.dates.DateFormatter('%d/%m/%y')
        axes = plt.gca()
        axes.legend(self.senders + [ x + " : Average" for x in self.senders])
        axes.xaxis.set_major_formatter(formatter)
        plt.show()

def char_count_filter(msg):
    return len(msg["body"])

def message_count_filter(msg):
    return 1

# To be used with a lambda construction for a filtering function for a specific word
# see below
def word_count_filter(msg, word):
    return msg["body"].lower().count(word.lower())

# parses a whatsapp text file with name 'chat.txt'
# then plots a graph of the use of the word 'the', separated by sender over time

if __name__ == "__main__":
    x = WhatsParse("chat.txt")
    x.graph_over_time(lambda x : word_count_filter(x, "the"))