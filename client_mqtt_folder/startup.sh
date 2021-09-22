#!/bin/bash

# on relance le script en root
#[ `whoami` = root ] || exec sudo $0 $*

# on fait les vérifications pour gérer quand le conteneur se lancera
# sleep 100
# "/wait"

# on lance le programme
python3 -u mqtt_client_publisher.py
