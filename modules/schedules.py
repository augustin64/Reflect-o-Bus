import configparser
import datetime
import os
import shutil
from pathlib import Path, PurePath

from modules.lepilote import rtm

HOME = str(Path.home())
configpath = PurePath(HOME).joinpath(".config/reflect-o-bus/")

if not os.path.isfile(configpath.joinpath("config")):
    os.makedirs(configpath, exist_ok=True)
    shutil.copy("./examples/default", configpath.joinpath("config"))


class Configuration:
    def __init__(self):
        CONFIG_PARSER.read(configpath.joinpath("config"))
        self.schedules = CONFIG_PARSER["DEFAULT"]["schedules"].split(" ")
        schedules = []
        for i in CONFIG_PARSER.sections():
            if i.split("/")[0] == "schedule" and i.split("/")[1] in self.schedules:
                schedules.append(i.split("/")[1])
        self.categories = [CONFIG_PARSER["DEFAULT"]["default_category"]]
        self.schedules_by_category = int(
            CONFIG_PARSER["DEFAULT"]["schedules_by_category"]
        )
        self.lines = []
        self.pass_colors = CONFIG_PARSER["ADVANCED"]["pass_colors"]
        self.line_colors = CONFIG_PARSER["ADVANCED"]["lines_color"]
        for i in schedules:
            temp = {
                "publiccode": CONFIG_PARSER["schedule/" + i]["publiccode"],
                "direction": CONFIG_PARSER["schedule/" + i]["direction"],
                "stop": CONFIG_PARSER["schedule/" + i]["stop"],
            }
            try:
                temp["category"] = CONFIG_PARSER["schedule/" + i]["category"]
                if temp["category"] not in self.categories:
                    self.categories.append(temp["category"])
            except:
                temp["category"] = CONFIG_PARSER["DEFAULT"]["default_category"]

            self.lines.append(temp)

    def update(self):
        self.update_lines()

    def update_lines(self):
        # On récupère les lignes qui nous intéressent
        for i, _ in enumerate(self.lines):
            self.lines[i]["line"] = rtm.Line(
                {"PublicCode": self.lines[i]["publiccode"]}
            )

        for i in self.lines:
            i["line"].get_routes()
        # On récupère les arrêts qui nous intéressent
        delete_range = 0
        for i in range(len(self.lines)):
            k = i - delete_range
            routes = []
            for j in self.lines[k]["line"].routes:
                if j.DirectionStations == self.lines[k]["direction"]:
                    routes.append(j)
            if len(routes) == 0:
                print(
                    f"Can't find satisfying route for {self.lines[k]['publiccode']}, removing it"
                )
                self.lines.remove(self.lines[k])
                delete_range += 1
            else:
                self.lines[k]["route"] = routes[0]

        _ = [i["route"].get_stops() for i in self.lines]
        delete_range = 0

        for i in range(len(self.lines)):
            k = i - delete_range
            stops = [
                j
                for j in self.lines[k]["route"].stops
                if j.Name == self.lines[k]["stop"]
            ]

            if len(routes) == 0:
                print(
                    f"Can't find satisfying route for {self.lines[k]['publiccode']}, removing it"
                )
                self.lines.remove(self.lines[k])
                delete_range += 1

            else:
                if len(stops) != 0:
                    self.lines[k]["stop"] = stops[0]
                else:
                    print(
                        f"Can't find satisfying stop for '{self.lines[k]['stop']}', removing it"
                    )
                    self.lines.remove(self.lines[k])
                    delete_range += 1


def get_schedules(config):
    schedules = {}
    # On récupère l'horaire actuel en minutes à compter de minuit
    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds = (now - midnight).seconds

    for i in config.categories:  # On répète l'opération avec chaque catégorie
        for j in config.lines:  # On teste avec chaque ligne
            if (
                j["category"] == i
            ):  # Si la ligne est dans la catégorie dans laquelle nous itérons
                schedule = j["stop"].get_realtime_schedule()
                # Dans ce cas on commence par récupérer ses horaires en temps réel
                # Et si il n'y en a pas
                # On les rajoute (créant la liste si il n'existe pas déja)
                if len(schedule) == 0:
                    if i in schedules:
                        for k in j["stop"].get_theoric_schedule():
                            schedules[i].append((j["line"], k, False))
                    else:
                        schedules[i] = [
                            (j["line"], k, False)
                            for k in j["stop"].get_theoric_schedule()
                        ]
                else:
                    if not i in schedules:
                        schedules[i] = []
                    for k in schedule:  # Je comprends enfin ce que j'ai fait :)
                        schedules[i].append((j["line"], k, True))
                        # On rajoute les horaires dans la liste (contenant également les informations sur la ligne)

        if i in schedules.keys():
            new_schedules = []
            if len(schedules[i]) != 0:
                if schedules[i][0][1].RealTimeStatus == 1:
                    for j in schedules[i]:
                        if (
                            j[1].RealDepartureTime is not None
                            and j[1].RealDepartureTime >= seconds // 60
                        ):
                            new_schedules.append(
                                (j[0], j[1].RealDepartureTime - seconds // 60, j[2])
                            )
                else:
                    for j in schedules[i]:
                        if (
                            j[1].TheoricDepartureTime is not None
                            and j[1].TheoricDepartureTime >= seconds // 60
                        ):
                            new_schedules.append(
                                (j[0], j[1].TheoricDepartureTime - seconds // 60, j[2])
                            )
                schedules[i] = new_schedules
            else:
                schedules[i] = []
            # On trie les horaires en fonction de leur horaire et on en garde le nombre défini
            schedules[i] = sorted(schedules[i], key=lambda tup: (tup[1]))[
                : config.schedules_by_category
            ]
            # Si les couleurs ne doivent pas être passées d'après le fichier de configuration,
            # on remplace alors leur couleur par une couleur unie, définie das le fichier de configuration
            if config.pass_colors != "True":
                for j in schedules[i]:
                    item = j[0]
                    item.color = config.line_colors
                    j = (item, j[1])

    return schedules


class Schedules:
    def __init__(self):
        global CONFIG_PARSER
        CONFIG_PARSER = configparser.ConfigParser()

        self.config = Configuration()
        self.config.update()
        print(" * Config Initialized")

    def __main__(self):
        schedules = get_schedules(self.config)
        return schedules
