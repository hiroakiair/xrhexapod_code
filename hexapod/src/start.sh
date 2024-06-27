#!/bin/sh
sleep 10
cd /home/pi/work/udev-monitor/
node main.js > /home/pi/work/hexapod/logs/stream.log 2>&1 &
sleep 2
echo "123456" | sudo -S pigpiod
sleep 1
cd /home/pi/work/hexapod/src/
nohup python3 -u ./xrtsengine.py > /home/pi/work/hexapod/logs/engine.log 2>&1 &
