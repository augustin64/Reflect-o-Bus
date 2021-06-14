#!/bin/bash

xset s off
xset -dpms
xset s noblank

unclutter -idle 1 -jitter 2 -root &
GUC="gunicorn --bind 0.0.0.0:5000 wsgi:app"
nohup $GUC > /root/logs/gunicorn.txt &
exec dwm &
sleep 3 && midori -e Fullscreen -a http://localhost:5000/boot > /root/logs/midori.txt