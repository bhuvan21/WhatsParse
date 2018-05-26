import sys
from datetime import datetime, timedelta
from time import time
from copy import deepcopy
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from tqdm import tqdm
from scipy import stats

DATE_FORMAT = "%d/%m/%Y"

plotly.tools.set_credentials_file(username='bhuvan21', api_key='wSlOaVC9UvnoZk1rW4zr')

SUBJECT_CHANGE = "changed the subject to"
DESC_CHANGE = "changed the group description"
ICON_CHANGE = "changed this group's icon"


start = time()

class Chat():
    def __init__(self, filename):
        self.file = open(filename, "r", encoding="utf-8")
        self.you = "Ash Belur"
        self.get_data()

    def get_data(self):
        self.filter_bad_things()
        self.get_participants()
        self.get_others()

            
    def filter_bad_things(self):
        text = self.file.read()
        self.text = ''.join([i if ord(i) < 128 else '?' for i in text])
        
        parts = []
        message = ""
        for line in tqdm(text.split("\n"), ncols=100, desc="Separating txt into parts"):
            try:
                if "[" in line and "]" in line and ":" in line and line.index("]") - line.index("[") == 21:
                    if message != "":
                        formatted = ''.join([i if ord(i) < 128 else '' for i in message])
                        parts.append(formatted)
                        message = ""
                        
                    message += line + "\n"
                
            except ValueError:
                message += line + "\n"
            
        self.chat_name = parts[0].split("]")[1].split(":")[0][1:]
        parts = parts[1:]

        for part in tqdm(parts, ncols=100, desc="filtering"):
            if len(part) == 0:
                parts.remove(part)
                break

            if part[-1] == "\n":
                parts[parts.index(part)] = part[:-1]

        self.parts = parts

    def get_participants(self):
        name = ""
        self.names = []
        for message in self.parts:
            try:
                if len(message.split("]")) == 2 and len(message.split("]")[1].split(":")) == 2 and len(message.split(":")) == 4:
                    name = message.split("]")[1].split(":")[0][1:]
            except IndexError:
                pass
            if name != "":

                if name not in self.names:
                    self.names.append(name)

        for name in self.names:
            for name2 in self.names:
                if name in name2 and name != name2:
                    if len(name2) > 10:
                        self.names.remove(name2)

        if len(self.names) == 2:
            not_you = ""
            for name in self.names:
                if name != self.you: not_you = name
            self.chat_name = not_you


        
                    
    def get_others(self):
        self.x = 0
        self.added = []
        self.removed = []
        self.desc_changes = []
        self.name_changes = []
        self.messages = []
        self.lefts = []
        self.icon_changes = []
        for part in tqdm(self.parts, desc="Recognising parts"):

            part_dict = {}
            try:
                part_dict["hour"] = part.split(",", 1)[1][1:3]
                part_dict["minute"] = part.split(",", 1)[1][4:6]
                part_dict["second"] = part.split(",", 1)[1][7:9]
                part_dict["date"] = datetime.strptime(part.split(",", 1)[0][1:], DATE_FORMAT)
            except (IndexError, ValueError) as e:
                continue
            if "added" in part and len(part.split(":")) == 3:
                part_dict["type"] = "addition"
                part_dict["adder"] = part.split("]")[1].split("added")[0][1:-1]
                part_dict["added"] = part.split("added")[1][1:]
                self.added.append(part_dict)
            elif "removed" in part and len(part.split(":")) == 3:
                part = part.replace("You", self.you)
                part_dict["type"] = "removal"
                part_dict["remover"] = part.split("]")[1].split("removed")[0][1:-1]
                part_dict["removed"] = part.split("removed")[1][1:]
                self.removed.append(part_dict)
            elif SUBJECT_CHANGE in part:
                part = part.replace("You", self.you)
                part_dict["type"] = "subject_change"
                part_dict["changer"] = part.split(SUBJECT_CHANGE)[0].split("]")[1][1:-1]
                part_dict["name"] = part.split(SUBJECT_CHANGE)[1][1:]
                self.name_changes.append(part_dict)
            elif DESC_CHANGE in part:
                part = part.replace("You", self.you)
                part_dict["type"] = "desc_change"
                part_dict["changer"] = part.split("]")[1].split(DESC_CHANGE)[0]
                self.desc_changes.append(part_dict)
            elif "deleted the group description" in part:
                part = part.replace("You", self.you)
                part_dict["type"] = "desc_change"
                part_dict["changer"] = part.split("]")[1].split("deleted the group description")[0]
                self.desc_changes.append(part_dict)
            elif "left" in part:
                left = False
                for name in self.names:
                    if part.split("]", 1)[1] == " " + name + " left": left = True
                if left:
                    part_dict["type"] = "left"
                    part_dict["leaver"] = part.split("]", 1)[1][1:-5]
                    self.lefts.append(part_dict)
                else:
                    pass
            elif ICON_CHANGE in part:
                part = part.replace("You", self.you)
                part_dict["type"] = "icon_change"
                part_dict["changer"] = part.split("]")[1].split(ICON_CHANGE)[0][1:-1]
                self.icon_changes.append(part_dict)
            elif "deleted this group's icon" in part:
                part = part.replace("You", self.you)
                part_dict["type"] = "icon_change"
                part_dict["changer"] = part.split("]")[1].split("deleted this group's icon")[0][1:-1]
                self.icon_changes.append(part_dict)
            elif "created this group" in part or "created group" in part:
                pass
            elif "now an admin" in part:
                pass
            else:
                if "PM" in part[:21] or "AM" in part[:21]:
                    try:
                        self.names.remove(part.split("[", 1)[1].split(":", 1)[0][1:])
                    except ValueError:
                        pass
                else:
                    try:
                        part_dict["sender"] = part.split("]")[1].split(":")[0][1:]
                        part_dict["text"] = part.split(":", 3)[3][1:]
                        part_dict["media"] = False
                        if ("<" in part_dict["text"] and ">" in part_dict["text"] and "omitted" in part_dict["text"]) or "<‎attached>" in part_dict["text"]:
                            part_dict["media"] = True
                        self.messages.append(part_dict)
                    except:
                        print(part)
                        continue




    def get_summary(self):
        print("Summary of the chat '{}'".format(self.chat_name))
        print("This chat has had {} members:".format(len(self.names)))
        for name in self.names:
            print(name)
        print("This chat has seen {} messages over the {} days it has been active".format(len(self.messages), self.get_duration()))
        print("{} of these messages were messages containing some media".format(self.media_messages()))
        self.get_spam_rankings()

        print("The name has been changed {} times".format(len(self.name_changes)))
        print("It has been:")
        names = []
        for change in self.name_changes:
            if change["name"] not in names:
                names.append(change["name"])
                print(change["name"])
        
        print("The description has been changed {} times".format(len(self.desc_changes)))
        print("The icon has been changed {} times".format(len(self.icon_changes)))
                
    def get_duration(self):
        delta = self.messages[-1]["date"] - self.messages[0]["date"]
        print(self.messages[-1], self.messages[0])
        return delta.days
    
    def media_messages(self):
        count = 0
        for message in self.messages:
            if message["media"]: count += 1

        return count

    def get_ratios(self, mode="messages"):
        ratios = {}
        for name in self.names:
            ratios[name] = 0

        for message in self.messages:
            if mode == "messages":
                ratios[message["sender"]] += 1
            elif mode == "media":
                if message["media"]:
                    ratios[message["sender"]] += 1
            elif mode == "chars":   
                ratios[message["sender"]] += len(message["text"])
        
        
        return ratios

    def get_spam_rankings(self):
        print("Here are the spam rankings for {}".format(self.chat_name))
        ratios = self.get_ratios()
        print("By messages sent:")
        
        s = [(k, ratios[k]) for k in sorted(ratios, key=ratios.get, reverse=True)]
        for rank, person in enumerate(s):
            if person[1] != 0:
                rank += 1
                print("{}. {} sent {} messages".format(rank, person[0], person[1]))
        print()

        print("By media")
        ratios = self.get_ratios(mode="media")
        s = [(k, ratios[k]) for k in sorted(ratios, key=ratios.get, reverse=True)]
        for rank, person in enumerate(s):
            if person[1] != 0:
                rank += 1
                print("{}. {} sent {} media messages".format(rank, person[0], person[1]))
        print()

        print("By characters\n")
        ratios = self.get_ratios(mode="chars")
        s = [(k, ratios[k]) for k in sorted(ratios, key=ratios.get, reverse=True)]
        for rank, person in enumerate(s):
            if person[1] != 0:
                rank += 1
                print("{}. {} sent {} characters".format(rank, person[0], person[1]))
        print()


    def get_average_chars(self):
        message_ratios = self.get_ratios()
        char_ratios = self.get_ratios(mode="chars")
        ratios = {}
        for (name, messages), (name2, chars) in zip(message_ratios.items(), char_ratios.items()):
            ratios[name] = int(chars/messages)
        
        s = [(k, ratios[k]) for k in sorted(ratios, key=ratios.get, reverse=True)]
        ratios = {}
        for name, val in s:
            ratios[name] = val
        
        return ratios

    def make_pie_charts(self):
        ratios = self.get_ratios("chars")
        labels = list(ratios.keys())
        values = list(ratios.values())



        trace = go.Pie(labels=labels, values=values)

        py.plot([trace], filename=self.chat_name+ " activity by person")

    def average_chars_bar(self):
        
        ratios = self.get_average_chars()
        data = [go.Bar(
            x=list(ratios.keys()),
            y=list(ratios.values()))]
        
        py.plot(data, filename='Average chars per message')

    def generate_x_axis(self, date1, date2):
        delta = date2 - date1
        x = []
        for i in range(delta.days):
            x.append(i)
        
        return x

    def get_blols(self):
        total = 0
        for message in self.messages:
            if "Bhuvan" in message["sender"]:
                count = message["text"].lower().count("lol")
                total += count
        return total

    def all_time_graph(self, mode="messages"):
        #print(time()-start, "alltimegraph")
        days = []
        day = []
        date = ""
        for message in tqdm(self.messages, "Sorting by date"):
            if self.messages.index(message)%1000 == 0 :print("{} / {}".format(self.messages.index(message), len(self.messages)))
            date = message["date"]
            #print(time()-start, "try")v
            try:
                next_date = self.messages[self.messages.index(message)+1]["date"]
            except IndexError:
                next_date = date
            #print(time()-start, "except")
            #print("d")
            if next_date != date:
                day.append(message)
                #if day == []: print("Oh no")
                days.append(day)
                day = []
            else:
                day.append(message)


        #print(days[-1])
        #print(time()-start, "second loop")
        for day in tqdm(days, desc="Filling in empty days"):
            n = days.index(day)
            #if n%1000 == 0 :print("{} / {}".format(n, len(days)))
            next_day = days[min(n+1, len(days)-1)]
            #print(day[0])
            #print(time()-start, "try")
            try:
                delta = next_day[0]["date"] - day[0]["date"]
                print(delta)
            except:
                continue

            
            if delta.days > 1:
                i = 0
                date = deepcopy(day[0]["date"])
                print(delta.days)
                for i in range(delta.days-1):
                    i += 1
                    date += timedelta(days=1)
                    days.insert(days.index(day)+i, [])
            
        print(len(days))
        
        
        x = self.generate_x_axis(days[0][0]["date"], days[-1][0]["date"])
        
        
        ys = {}
        for name in self.names:
            ys[name] = []

        for day in days:
            ratios = {}
            for name in self.names:
                ratios[name] = 0
            if day != []:
                for message in day:
                    if mode == "messages":
                        ratios[message["sender"]] += 1
                    elif mode == "characters":
                        ratios[message["sender"]] += len(message["text"])
            

            
            for key, val in ratios.items():
                ys[key].append(val)


        print(ys)

        
        traces = []
        for name in self.names:
            trace = go.Scatter(
                x=x,
                y=ys[name],
                name=name
            )
            traces.append(trace)

        layout = go.Layout(
            title='Activity',
            xaxis=dict(
                title='Day (from inception)',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title=mode.capitalize(),
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
        
        

        fig = go.Figure(data=traces, layout=layout)
        return py.plot(fig, filename="test1")
        
