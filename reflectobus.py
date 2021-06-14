import configparser
import io
import os
import json
from pathlib import Path, PurePath
import socket
import zipfile

import requests
from flask import (Flask, make_response, redirect, render_template, request,
                   url_for, send_file)

from modules import schedules
from modules.lepilote import rtm

# On initialise le serveur Flask
app = Flask(__name__)

def set_config(data):
    # New config parser object
    newConfig = configparser.ConfigParser()
    # Downloading image if is url
    if data['ADVANCED']['background_url'][:4] == "http" :
        response = requests.get(data['ADVANCED']['background_url'])
        file = open("./static/walls/"+data['ADVANCED']['background_url'].split('/')[-1], "wb")
        file.write(response.content)
        file.close()
        data['ADVANCED']['background_url'] = data['ADVANCED']['background_url'].split('/')[-1]
    # writing all config data to the new config parser object
    for i in data.keys():
        newConfig[i] = data[i]
    # writing object to file
    with open(configpath.joinpath('config'), 'w') as configfile:
        newConfig.write(configfile)
    # reloading changes
    reload_config()
    return ("Configuration actualisée")

def reload_config():
    global config_changed
    global configParser
    config_changed = True
    configParser = configparser.ConfigParser()
    configParser.read(configpath.joinpath('config'))

def get_config():
    cfg = {'DEFAULT':{},'ADVANCED':{}}
    for i in configParser['DEFAULT'] :
        cfg['DEFAULT'][i] = configParser['DEFAULT'][i]
    for i in configParser.sections() :
        cfg[i] = {}
        for j in configParser[i] :
            if j not in configParser['DEFAULT'].keys() :
                cfg[i][j] = configParser[i][j]

    return cfg

def set_wlan(data):
    # NotImplementedError
    return("WLAN changé")

def get_routes(data):
    line_object = schedules.rtm.Line(data)
    routes = line_object.get_routes()
    data = {}
    for i in routes :
        data[i.refNEtex] = i.DirectionStationsSqli

    return data

def get_stops(data):
    url = 'https://api.rtm.fr/front/getStations/' + data['refNEtex']
    content = eval(requests.get(url, headers=headers).text)['data']
    data = {}

    for i in content :
        data[i['refNEtex']] = i['Name']

    return data

def shutdown(data):
    return os.system('sudo shutdown now')

@app.route("/")
def index():
    data = {}
    return render_template('index.html',data=data)

@app.route("/boot")
def boot():
    localip = "127.0.0.1"
    if not offline: # We open a socket to get our ip on the local network
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localip = (s.getsockname()[0])
        s.close()

    data = {"version":ver,
            "rtm_version":rtm_ver,
            "boot_time":configParser['ADVANCED']['boot_time'],
            "local_ip":localip
    }
    data['background_color'] = configParser['ADVANCED']['background_color']
    return render_template('boot.html', data=data)

@app.route("/horaires")
def horaires():
    data={}
    global config_changed
    global schedules_object
    # fetching parsed data

    if not offline :
        if config_changed :
            schedules_object = schedules.Schedules()
            config_changed = False
        data['schedule'] = schedules_object.__main__()
    else : # We create fake Lines to be able to test the app when offline

        line_1 = schedules.rtm.Line({
            'name':"",
            'id':"7",
            'Carrier':"",
            'Operator':"RTM",
            'PublicCode':"7",
            'TypeOfLine':"",
            'VehicleType':"bus",
            'night':"false",
            'lepiloteId':"RTM:LNE:xx",
            'color':"#FBBA00",
            'sqliType':"bus"
        })
        line_2 = schedules.rtm.Line({
            'name':"",
            'id':"9",
            'Carrier':"",
            'Operator':"RTM",
            'PublicCode':"9",
            'TypeOfLine':"",
            'VehicleType':"bus",
            'night':"false",
            'lepiloteId':"RTM:LNE:xx",
            'color':"#189B52",
            'sqliType':"bus"
        })
        if not bool(configParser['ADVANCED']['pass_colors']) :
            line_1.color = configParser['ADVANCED']['lines_color']
            line_2.color = configParser['ADVANCED']['lines_color']

        cat_1, cat_2 = [("",0)], [("",0)]
        for _ in range(int(configParser['DEFAULT']['schedules_by_category'])) :
            cat_1.append((line_1,random.randint(cat_1[-1][1],cat_1[-1][1]+15),False))
            cat_2.append((line_2,random.randint(cat_2[-1][1],cat_2[-1][1]+15),False))
        
        data['schedule'] = {"category1":cat_1[1:],
                            "category2":cat_2[1:]
                            }

    data['refresh_time'] = configParser['ADVANCED']['refresh_time']
    data['background_color'] = configParser['ADVANCED']['background_color']
    if configParser['ADVANCED']['background_type'] == "image" :
        data['background_url'] = configParser['ADVANCED']['background_url']

    data['total_schedules'] = 0
    for i in data['schedule'].keys():
        data['total_schedules'] += len(data['schedule'][i])

    if data['total_schedules'] == 0 :
        localip = "127.0.0.1"
        if not offline:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            localip = (s.getsockname()[0])
            s.close()

        data['localip'] = localip

    return render_template('horaires.html',data=data)

# not in use yet
@app.route('/get')
def get():
    actions = {
        "config":get_config,
    }
    content = request.args.get("content")
    if content in actions.keys():
        return actions[content]()
            

    else :
        return "content is undefined"

# get json posted data
@app.route('/post', methods = ['POST'])
def postJsonHandler():
    actions = {
        "setConfig": set_config,
        "set_WLAN": set_wlan,
        "getRoutes":get_routes,
        "getStops":get_stops,
        "shutdown":shutdown,
    }
    if (request.is_json) :
        content = request.get_json()
        action = content['action']
        data = content['data']
        return actions[action](data)

@app.route("/config")
def config():
    # Planning to add some in-browser config
    return render_template('config.html')

@app.route("/get-logs")
def get_logs():
    logs_path = PurePath.joinpath(Path.home(),'logs')
    data = io.BytesIO()

    with zipfile.ZipFile(data, mode='w') as zf:
        for file in Path(logs_path).rglob('*'): # Cette solution supprime
            zf.write(file, file.name)           # la possibilité d'utiliser des dossiers dans 
    data.seek(0)                                # les logs, mais ce n'est pas quelque chose de nécessaire

    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='logs.zip'
    )

@app.errorhandler(500)
def server_error_handler(e):
    print("error:",e)
    return render_template('error_500.html',data=e)


# Development option to run tests without internet access
global offline
offline = False
if offline :
    # on importe ce module uniquement dans le cas où le mode "offline" est activé
    # ce n'est pas une méthode très propre masin le mode de développement sera
    # supprimé prochainement
    import random

# On importe le fichier de configuration
# qui esdt crée par le sous-module "schedules" si il n'existe pas encore
home = str(Path.home())
configpath = PurePath(home).joinpath('.config/reflect-o-bus/')

configParser = configparser.ConfigParser()
configParser.read(configpath.joinpath('config'))


# setting custom headers
headers = {'User-Agent':'Reflect-o-Bus Client', 'From':'https://github.com/augustin64/Reflect-o-Bus'}
# Initializing schedules

if not offline :
    config_changed = True
else:
    print(' * Running offline mode')

# get apps versions :
with open('./.git/refs/heads/main','r') as f:
    ver = f.read().replace('\n','')
with open('./.git/modules/modules/lepilote/refs/heads/main','r') as f:
    rtm_ver = f.read().replace('\n','')


if __name__ == "__main__":
    app.run(host='0.0.0.0')