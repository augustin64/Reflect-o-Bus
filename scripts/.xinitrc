#!/bin/bash

xset s off
xset -dpms
xset s noblank
xrandr --output HDMI-1 --rotate left &

while read var sep value
do
    if [[ "$var" = *"port"* ]]; then
        port="$value"
    fi;
done < "$HOME/.config/reflect-o-bus/config"

if [[ "$port" = "" ]]; then
    port="5000"
fi;

unclutter -idle 1 -jitter 2 -root &
GUC="gunicorn --bind 0.0.0.0:$port wsgi:app"
nohup $GUC > /root/logs/gunicorn.txt &
exec dwm &
sleep 3 && midori -e Fullscreen -a http://localhost:$port/boot > /root/logs/midori.txt