#!/usr/bin/python3
"""
Fichier python principal, contenant le serveur Flask
"""
import configparser
import io
import os
import socket
import zipfile
from pathlib import Path, PurePath

import requests
from flask import Flask, render_template, request, send_file

from modules import schedules
from modules import configchecker

# On initialise le serveur Flask
app = Flask(__name__)


def get_ip():
    """
    Renvoie l'ip locale du serveur
    """
    localip = "127.0.0.1"
    if not OFFLINE:  # We open a socket to get our ip on the local network
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        localip = sock.getsockname()[0]
        sock.close()
    return localip


def fake_schedules(datatype="object"):
    """
    Générateur de fausses lignes de bus, gagnerait à être amélioré
    """
    if datatype == "object":
        cat_1, cat_2 = [("", 0)], [("", 0)]

        line_1 = schedules.rtm.Line(
            {
                "name": "",
                "id": "7",
                "Carrier": "",
                "Operator": "RTM",
                "PublicCode": "7",
                "TypeOfLine": "",
                "VehicleType": "bus",
                "night": "false",
                "lepiloteId": "RTM:LNE:xx",
                "color": "#FBBA00",
                "sqliType": "bus",
            }
        )
        line_2 = schedules.rtm.Line(
            {
                "name": "",
                "id": "9",
                "Carrier": "",
                "Operator": "RTM",
                "PublicCode": "9",
                "TypeOfLine": "",
                "VehicleType": "bus",
                "night": "false",
                "lepiloteId": "RTM:LNE:xx",
                "color": "#189B52",
                "sqliType": "bus",
            }
        )

        if CONFIG_PARSER["ADVANCED"]["pass_colors"] != "True":
            line_1.color = CONFIG_PARSER["ADVANCED"]["lines_color"]
            line_2.color = CONFIG_PARSER["ADVANCED"]["lines_color"]

        for _ in range(int(CONFIG_PARSER["DEFAULT"]["schedules_by_category"])):
            cat_1.append(
                (line_1, random.randint(cat_1[-1][1], cat_1[-1][1] + 15), False)
            )
            cat_2.append(
                (line_2, random.randint(cat_2[-1][1], cat_2[-1][1] + 15), False)
            )

    elif datatype == "JSON":
        cat_1, cat_2 = [{"hour": 0}], [{"hour": 0}]

        line_1 = {
            "name": "",
            "id": "7",
            "Carrier": "",
            "Operator": "RTM",
            "PublicCode": "7",
            "TypeOfLine": "",
            "VehicleType": "bus",
            "night": "false",
            "lepiloteId": "RTM:LNE:xx",
            "color": "#FBBA00",
            "sqliType": "bus",
        }
        line_2 = {
            "name": "",
            "id": "9",
            "Carrier": "",
            "Operator": "RTM",
            "PublicCode": "9",
            "TypeOfLine": "",
            "VehicleType": "bus",
            "night": "false",
            "lepiloteId": "RTM:LNE:xx",
            "color": "#189B52",
            "sqliType": "bus",
        }

        for _ in range(int(CONFIG_PARSER["DEFAULT"]["schedules_by_category"])):
            line_1["hour"] = random.randint(cat_1[-1]["hour"], cat_1[-1]["hour"] + 15)
            line_2["hour"] = random.randint(cat_2[-1]["hour"], cat_2[-1]["hour"] + 15)
            line_1["isRealTime"] = False
            line_2["isRealTime"] = False
            cat_1.append(line_1)
            cat_2.append(line_2)

    schedule = {"category1": cat_1[1:], "category2": cat_2[1:]}
    return schedule


def set_config(data):
    """
    Met à jour le fichier de configuration dans `$HOME/.config/reflect-o-bus/`
    à partir des infos entrées par l'utilisateur sur la page `/config`
    """
    # New config parser object
    new_config = configparser.ConfigParser()
    # Downloading image if is url
    if data["ADVANCED"]["background_url"][:4] == "http":
        response = requests.get(data["ADVANCED"]["background_url"])
        img_path = "./static/walls/" + data["ADVANCED"]["background_url"].split("/")[-1]
        with open(img_path, "wb") as file:
            file.write(response.content)
            file.close()
        data["ADVANCED"]["background_url"] = data["ADVANCED"]["background_url"].split(
            "/"
        )[-1]
    # writing all config data to the new config parser object
    for i in data.keys():
        new_config[i] = data[i]
    # writing object to file
    with open(configpath.joinpath("config"), "w") as configfile:
        new_config.write(configfile)
    # reloading changes
    reload_config()
    return "Configuration actualisée"


def reload_config():
    """
    Recharge la configuration de manière globale
    """
    global CONFIG_CHANGED
    global CONFIG_PARSER
    CONFIG_CHANGED = True
    CONFIG_PARSER = configparser.ConfigParser()
    CONFIG_PARSER.read(configpath.joinpath("config"))


def get_config():
    """
    Renvoie la configuration de `$HOME/.config/reflect-o-bus/`
    Sous format json (type dict de python)
    """
    cfg = {"DEFAULT": {}, "ADVANCED": {}}
    for i in CONFIG_PARSER["DEFAULT"]:
        cfg["DEFAULT"][i] = CONFIG_PARSER["DEFAULT"][i]
    for i in CONFIG_PARSER.sections():
        cfg[i] = {}
        for j in CONFIG_PARSER[i]:
            if j not in CONFIG_PARSER["DEFAULT"].keys():
                cfg[i][j] = CONFIG_PARSER[i][j]

    return cfg


def get_horaires():
    """
    Renvoie les horaires récupérées depuis le module `schedules`
    """
    data = {}
    data["config"] = {
        "refresh_time": CONFIG_PARSER["ADVANCED"]["refresh_time"],
        "hide_category": (CONFIG_PARSER["ADVANCED"]["hide_category"] == "True"),
        "pass_colors": (CONFIG_PARSER["ADVANCED"]["pass_colors"] == "True"),
        "lines_color": CONFIG_PARSER["ADVANCED"]["lines_color"],
        "localip": get_ip(),
        "shape": CONFIG_PARSER["ADVANCED"]["shape"],
    }
    if not OFFLINE:
        global CONFIG_CHANGED
        global SCHEDULES_OBJECT
        if CONFIG_CHANGED:
            SCHEDULES_OBJECT = schedules.Schedules()
            CONFIG_CHANGED = False
        schedules_data = SCHEDULES_OBJECT.__main__()
        data["schedule"] = {}

        for category in schedules_data:
            data["schedule"][category] = []
            for hour in schedules_data[category]:
                data["schedule"][category].append(
                    {
                        "name": hour[0].name,
                        "id": hour[0].id,
                        "Carrier": hour[0].Carrier,
                        "Operator": hour[0].Operator,
                        "PublicCode": hour[0].PublicCode,
                        "TypeOfLine": hour[0].TypeOfLine,
                        "VehicleType": hour[0].VehicleType,
                        "night": hour[0].night,
                        "lepiloteId": hour[0].lepiloteId,
                        "color": hour[0].color,
                        "sqliType": hour[0].sqliType,
                        "hour": hour[1],
                        "isRealTime": hour[2],
                    }
                )
        return {"data": data, "content": "Horaires"}
    data["schedule"] = fake_schedules(datatype="JSON")
    return {"data": data, "content": "Horaires"}


def get_look():
    """
    Renvoie la partie graphique de la configuration,
    afin que l'actualisation côté client des modifications des paramètres
    se fasse plus fréquemment qu'à chaque rafraîchissement des horaires
    """
    data = {
        "background_color": CONFIG_PARSER["ADVANCED"]["background_color"],
        "font_size": (CONFIG_PARSER["ADVANCED"]["font_size"]),
        "refresh_time": (CONFIG_PARSER["ADVANCED"]["refresh_time"]),
    }
    if CONFIG_PARSER["ADVANCED"]["background_type"] == "image":
        data["background_url"] = CONFIG_PARSER["ADVANCED"]["background_url"]
    return {"data": data, "content": "look"}


def set_wlan(data):
    """
    Fonction inutile simulant une modification des
    paramètres sans fil
    """
    del data
    # NotImplementedError
    return "WLAN changé"


def get_routes(data):
    """
    Renvoie les directions disponible pour une ligne
    pour l'auto-complétion des trajets sur la page `/config`
    """
    line_object = schedules.rtm.Line(data)
    routes = line_object.get_routes()
    data = {}
    for i in routes:
        data[i.refNEtex] = i.DirectionStationsSqli
    return data


def get_stops(data):
    """
    Renvoie la liste des différents arrêts pour une direction d'une ligne de bus/métro/tram
    pour l'auto-complétion des trajets sur la page `/config`
    """
    url = "https://api.rtm.fr/front/getStations/" + data["refNEtex"]
    content = eval(requests.get(url, headers=headers).text)["data"]
    data = {}
    for i in content:
        data[i["refNEtex"]] = i["Name"]
    return data


def shutdown(data):
    """
    Permet d'éteindre le serveur depuis l'interface graphique
    """
    del data
    return os.system("sudo shutdown now")


@app.route("/")
def index():
    """
    Renvoie la page index
    """
    data = {}
    return render_template("index.html", data=data)


@app.route("/boot")
def boot():
    """
    Renvoie la page de boot avec les informations correspondantes
    (version git + adresse ip de la machine)
    """
    data = {
        "version": ver,
        "rtm_version": rtm_ver,
        "boot_time": CONFIG_PARSER["ADVANCED"]["boot_time"],
        "local_ip": get_ip(),
        "background_color": CONFIG_PARSER["ADVANCED"]["background_color"],
        "port": CONFIG_PARSER["ADVANCED"]["port"],
    }
    return render_template("boot.html", data=data)


@app.route("/horaires")
def horaires():
    """
    Renvoie le template des horaires, page noire appelant du javascript
    pour récupérer les horaires
    """
    data = {
        "local_ip": get_ip(),
        "port": CONFIG_PARSER["ADVANCED"]["port"],
    }
    return render_template("horaires.html", data=data)


# not in use yet
@app.route("/get")
def get():
    """
    Réponse aux différentes requêtes get du client javascript
    """
    actions = {
        "config": get_config,
        "horaires": get_horaires,
        "look": get_look,
    }
    content = request.args.get("content")
    if content in actions.keys():
        return actions[content]()
    return "content is undefined"


# get json posted data
@app.route("/post", methods=["POST"])
def post_json_handler():
    """
    Fonction convertissant les requêtes post en dictionnaire JSON
    """
    actions = {
        "setConfig": set_config,
        "set_WLAN": set_wlan,
        "getRoutes": get_routes,
        "getStops": get_stops,
        "shutdown": shutdown,
    }
    if request.is_json:
        content = request.get_json()
        action = content["action"]
        data = content["data"]
        return actions[action](data)
    return {}


@app.route("/config")
def config():
    """
    Renvoie la page de configuration vide, la configuration étant chargée
    par une requête GET
    """
    return render_template("config.html")


@app.route("/get-logs")
def get_logs():
    """
    Renvoie une archive zip contenant les logs du serveur
    """
    logs_path = PurePath.joinpath(Path.home(), "logs")
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode="w") as zip_file:
        for file in Path(logs_path).rglob("*"):  # Cette solution supprime
            zip_file.write(
                file, file.name
            )  # la possibilité d'utiliser des dossiers dans
    data.seek(0)  # les logs, car elle prend tous les fichiers
    # sans différencier leur chemin d'accès
    return send_file(
        data,
        mimetype="application/zip",
        as_attachment=True,
        attachment_filename="logs.zip",
    )


@app.route("/logs")
def view_logs():
    """
    Permet de naviguer parmi les logs sans avoir à les télécharger,
    avec une interface semblable à un serveur FTP
    """
    data = {}
    data["isLogs"] = False
    process = request.args.get("process")
    # $HOME/logs
    logs_path = PurePath.joinpath(Path.home(), "logs")
    if process is not None:
        data["process"] = process  # nom du fichier de logs
        if os.path.exists(PurePath.joinpath(logs_path, process + ".txt")):
            data["isLogs"] = True
            # On commence par regardetr si il existe un fichier de logs à
            # l'emplacement $HOME/logs/<process>.txt
            with open(PurePath.joinpath(logs_path, process + ".txt"), "r") as file:
                data["logs"] = str(file.read())
        elif os.path.exists(PurePath.joinpath(logs_path, process)):
            data["isLogs"] = True
            # Sinon, on regarde à l'emplacement $HOME/logs/<process>
            with open(PurePath.joinpath(logs_path, process), "r") as file:
                data["logs"] = str(file.read())
    if not data["isLogs"]:
        # Si aucun processus n'est demandé ou qu'il n'existe pas,
        # on renvoie la liste des processus disponibles
        data["available_logs"] = os.listdir(logs_path)
        for i in range(len(data["available_logs"])):
            if data["available_logs"][i][-4:] == ".txt":
                data["available_logs"][i] = data["available_logs"][i][:-4]
    return render_template("logs.html", data=data)


@app.errorhandler(500)
def server_error_handler(error):
    """
    Gère les erreurs internes du serveur en affichant l'erreur
    en question sur le client, réfraîchissant la page à intervalles réguliers
    """
    print("error:", error)
    print(request.base_url)
    if request.is_json or request.base_url.split("/")[-1] == "get":
        return error
    return render_template("error_500.html", data=error)


# Development option to run tests without internet access
global OFFLINE
OFFLINE = False
if OFFLINE:
    # on importe ce module uniquement dans le cas où le mode "offline" est activé
    # ce n'est pas une méthode très propre masin le mode de développement sera
    # supprimé prochainement
    import random

# On importe le fichier de configuration
# qui esdt crée par le sous-module "schedules" si il n'existe pas encore
HOME = str(Path.home())
configpath = PurePath(HOME).joinpath(".config/reflect-o-bus/")

CONFIG_PARSER = configparser.ConfigParser()
CONFIG_PARSER.read(configpath.joinpath("config"))

configchecker.check(configpath.joinpath("config"), "./examples/default")

# setting custom headers
headers = {
    "User-Agent": "Reflect-o-Bus Client",
    "From": "https://github.com/augustin64/Reflect-o-Bus",
}
# Initializing schedules

if not OFFLINE:
    CONFIG_CHANGED = True
else:
    print(" * Running offline mode")

# get apps versions :
with open("./.git/refs/heads/main", "r") as f:
    ver = f.read().replace("\n", "")
with open("./.git/modules/modules/lepilote/refs/heads/main", "r") as f:
    rtm_ver = f.read().replace("\n", "")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
