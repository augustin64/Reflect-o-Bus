import configparser
import json
import socket
from pathlib import Path, PurePath

from flask import (Flask, make_response, redirect, render_template, request,
                   url_for)

from modules import schedules
from modules.lepilote import rtm

# Development option to run tests without internet access
global offline
offline = False
if offline :
    # on importe ce module uniquement dans le cas où le mode "offline" est activé
    import random

# importing config file
# created by schedules submodule if empty
home = str(Path.home())
configpath = PurePath(home).joinpath('.config/reflect-o-bus/')
config_changed = False

configParser = configparser.ConfigParser()
configParser.read(configpath.joinpath('config'))

# initializing app
app = Flask(__name__)
# setting custom headers
headers = {'User-Agent':'MagicMirror rtm Client', 'From':'https://github.com/augustin64/MagicMirror-rtm'}
# Initializing schedules

if not offline :
    schedules_object = schedules.Schedules()
    print(" * Schedules Initialized")
else:
    print(' * Running offline mode')

# get apps versions :
with open('./.git/refs/heads/main','r') as f:
    ver = f.read().replace('\n','')
with open('./.git/modules/modules/lepilote/refs/heads/main','r') as f:
    rtm_ver = f.read().replace('\n','')

def set_config(data):
    # New config parser object
    newConfig = configparser.ConfigParser()
    # writing all config data to this object
    for i in data.keys():
        newConfig[i] = data[i]
    # writing object to file
    with open(configpath.joinpath('config'), 'w') as configfile:
        newConfig.write(configfile)
    # reloading changes
    reload_config()

def reload_config():
    global config_changed
    global configParser
    config_changed = True
    configParser = configparser.ConfigParser()
    configParser.read(configpath.joinpath('config'))

@app.route("/boot")
@app.route("/")
def boot():
    localip = "127.0.0.1"
    if not offline:
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
        data['schedule'] = schedules_object.__main__()
    else :

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
        for i in range(int(configParser['DEFAULT']['schedules_by_category'])) :
            cat_1.append((line_1,random.randint(cat_1[-1][1],cat_1[-1][1]+15)))
            cat_2.append((line_2,random.randint(cat_2[-1][1],cat_2[-1][1]+15)))
        
        data['schedule'] = {"category1":cat_1[1:],
                            "category2":cat_2[1:]
                            }

    data['refresh_time'] = configParser['ADVANCED']['refresh_time']
    data['background_color'] = configParser['ADVANCED']['background_color']
    if configParser['ADVANCED']['background_type'] == "image" :
        data['background_url'] = configParser['ADVANCED']['background_url']
    return render_template('horaires.html',data=data)

# not in use yet
@app.route('/get')
def get():
    content = request.args.get("content")
    if content == "config" :
        cfg = {'DEFAULT':{},'ADVANCED':{}}
        for i in configParser['DEFAULT'] :
            cfg['DEFAULT'][i] = configParser['DEFAULT'][i]
        for i in configParser.sections() :
            cfg[i] = {}
            for j in configParser[i] :
                if j not in configParser['DEFAULT'].keys() :
                    cfg[i][j] = configParser[i][j]

        return cfg
            

    else :
        return "content!=config"

# get json posted data
@app.route('/post', methods = ['POST'])
def postJsonHandler():
    actions = {
        "setConfig": set_config
    }
    if (request.is_json) :
        content = request.get_json()
        action = content['action']
        data = content['data']
        actions[action](data)
        return 'JSON posted'

@app.route("/config")
def config():
    # Planning to add some in-browser config
    return render_template('config.html')

if __name__ == "__main__":
    app.run(debug = False)
