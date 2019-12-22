#! /bin/bash

cd /home/pi/swpi3
logfile=./log/log`date '+%d%m%Y'`.log
sudo python3 -u swpi.py | tee -a $logfile

