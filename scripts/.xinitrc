#!/bin/bash

unclutter -idle 1 -jitter 2 -root &
export FLASK_HOST=0.0.0.0
nohup flask run > /root/logs/flask.txt 2>&1 &
exec dwm &
sleep 10 && midori -e Fullscreen -a http://localhost:5000 > /root/logs/midori.txt