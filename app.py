from flask import (Flask, make_response, redirect, render_template, request,
                   url_for)

from modules import schedules
from pathlib import Path, PurePath

from modules.rtm import rtm

home = str(Path.home())
configpath = PurePath(home).joinpath('.config/rtm-api/config')

# initializing app
app = Flask(__name__)
# setting custom headers
headers = {'User-Agent':'MagicMirror rtm Client', 'From':'https://github.com/augustin64/MagicMirror-rtm'}
# Initializing schedules
try :
    schedules_object = schedules.Schedules()
    print(" * Schedules Initialized")
except :
    schedules_object = None
    print(" * Running offline mode")

# get apps versions :
with open('./.git/refs/heads/main','r') as f:
    ver = f.read().replace('\n','')
with open('./.git/modules/rtm/refs/heads/main','r') as f:
    rtm_ver = f.read().replace('\n','')



@app.route("/boot")
@app.route("/")
def boot():
    data = {"version":ver,
            "rtm_version":rtm_ver
            }
    return render_template('boot.html', data=data)

@app.route("/horaires")
def horaires():
    # fetching parsed data
    sc = schedules_object.__main__()
    return render_template('index.html',data=sc)

# not in use yet
@app.route('/get')
def get():
    return ""

@app.route("/config")
def config():
    # Planning to add some in-browser config
    return render_template('config.html')

if __name__ == "__main__":
    app.run(debug = False)
