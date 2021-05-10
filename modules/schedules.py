import configparser
import datetime
import time

from modules.rtm import rtm

configParser = configparser.ConfigParser()

class Configuration():
    def __init__(self):
        configParser.read('config')
        self.refresh = int(configParser['DEFAULT']['refresh'])
        self.schedules = configParser['DEFAULT']['schedules'].split(' ')
        schedules = [ i.split('/')[1] for i in configParser.sections() if i.split('/')[0] == 'schedule' and i.split('/')[1] in self.schedules ]
        self.categories = [configParser['DEFAULT']['default_category']]
        self.schedules_by_category = int(configParser['DEFAULT']['schedules_by_category'])
        self.lines = []
        self.pass_colors = configParser['DEFAULT']['pass_colors']
        for i in schedules:
            temp = {
                "publiccode":configParser['schedule/'+i]['publiccode'],
                "direction":configParser['schedule/'+i]['direction'],
                "stop":configParser['schedule/'+i]['stop']
            }
            try :
                temp['category'] = configParser['schedule/'+i]['category']
                if temp['category'] not in self.categories :
                    self.categories.append(temp['category'])
            except :
                temp['category'] = configParser['DEFAULT']['default_category']

            self.lines.append(temp)

    def update(self):
        self.update_lines()

    def update_lines(self):
        # On récupère les lignes qui nous intéressent
        for i in range(len(self.lines)) :
            self.lines[i]['line'] = (rtm.Line({'PublicCode':self.lines[i]['publiccode']}))

        [i['line'].get_routes() for i in self.lines]
        # On récupère les arrêts qui nous intéressent
        delete_range = 0
        for i in range(len(self.lines)):
            k = i - delete_range
            routes = [ j for j in self.lines[k]['line'].routes if j.DirectionStationsSqli == self.lines[k]['direction']]
            if len(routes) == 0 :
                print("Can't find satisfying route for "+self.lines[k]['publiccode']+", removing it")
                self.lines.remove(self.lines[k])
                delete_range += 1
            else:
                self.lines[k]['route'] = routes[0]

        [i['route'].get_stops() for i in self.lines]
        delete_range = 0

        for i in range(len(self.lines)):
            k = i - delete_range
            stops = [ j for j in self.lines[k]['route'].stops if j.Name == self.lines[k]['stop']]

            if len(routes) == 0:
                print("Can't find satisfying route for "+self.lines[k]['publiccode']+", removing it")
                self.lines.remove(self.lines[k])
                delete_range += 1

            else:
                self.lines[k]['stop'] = stops[0]


def get_schedules(config):
    schedules = {}
    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds = (now - midnight).seconds

    for i in config.categories :
        for j in config.lines :
            if j['category'] == i :
                if i in schedules :
                    [ schedules[i].append((j['line'],k)) for k in j['stop'].get_schedule() ]
                else :
                    schedules[i] = [ (j['line'],k) for k in j['stop'].get_schedule() ]

        if i in schedules.keys() :
            schedules[i] = [(j[0],j[1].TheoricDepartureTime-seconds//60) for j in schedules[i] if j[1].TheoricDepartureTime != None and j[1].TheoricDepartureTime > seconds//60]
            schedules[i] = sorted(schedules[i], key=lambda tup:(tup[1], tup[0]))[:config.schedules_by_category]

    return schedules



class Schedules():
    def __init__(self):
        self.config = Configuration()
        self.config.update()

    def __main__(self):
        schedules = get_schedules(self.config)
        return schedules
