#!/bin/bash

cd /root/reflect-o-bus
git pull

# We update copied files
cp /root/reflect-o-bus/scripts/.xinitrc /root/.xinitrc
cp /root/reflect-o-bus/scripts/reflect-o-bus.service /etc/systemd/system/