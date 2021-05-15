import configparser
import json
import socket
from pathlib import Path, PurePath

from flask import (Flask, make_response, redirect, render_template, request,
                   url_for)

from modules import schedules
from modules.rtm import rtm

# importing config file
# created by schedules submodule if empty
home = str(Path.home())
configpath = PurePath(home).joinpath('.config/rtm-api/')
config_changed = False

configParser = configparser.ConfigParser()
configParser.read(configpath.joinpath('config'))

# initializing app
app = Flask(__name__)
# setting custom headers
headers = {'User-Agent':'MagicMirror rtm Client', 'From':'https://github.com/augustin64/MagicMirror-rtm'}
# Initializing schedules

schedules_object = schedules.Schedules()
print(" * Schedules Initialized")


# get apps versions :
with open('./.git/refs/heads/main','r') as f:
    ver = f.read().replace('\n','')
with open('./.git/modules/rtm/refs/heads/main','r') as f:
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
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localip = (s.getsockname()[0])
        s.close()
    except :
        print(' * Network unreachable')

    data = {"version":ver,
            "rtm_version":rtm_ver,
            "boot_time":configParser['ADVANCED']['boot_time'],
            "local_ip":localip
            }
    return render_template('boot.html', data=data)

@app.route("/horaires")
def horaires():
    data={}
    global config_changed
    global schedules_object
    # fetching parsed data
    if config_changed :
        schedules_object = schedules.Schedules()
    data['schedule'] = schedules_object.__main__()
    data['refresh_time'] = configParser['ADVANCED']['refresh_time']
    return render_template('index.html',data=data)

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
