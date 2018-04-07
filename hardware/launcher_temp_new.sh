#!/bin/sh

cd /home/pi/Documents/GeophoneDuino/

sudo /usr/bin/python /home/pi/Documents/GeophoneDuino/data_collection.py -l 192.168.0.112 192.168.0.113 192.168.0.114 192.168.0.115 -n 330
