#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/pyOBD_Anif_version
sudo python module2.py & python main.py
cd /
