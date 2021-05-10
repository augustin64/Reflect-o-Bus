from flask import (Flask, make_response, redirect, render_template, request,
                   url_for)

from modules import schedules

# initializing app
app = Flask(__name__)
# setting custom headers
headers = {'User-Agent':'MagicMirror rtm Client', 'From':'https://github.com/augustin64/MagicMirror-rtm'}
# Initializing schedules
schedules_object = schedules.Schedules()
print(" * Schedules Initialized")

@app.route("/index")
@app.route("/")
def home():
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
    return ("To implement")

if __name__ == "__main__":
    app.run(debug = False)
