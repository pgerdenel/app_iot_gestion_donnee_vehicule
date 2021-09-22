#!/bin/bash

# on relance le script en root
#[ `whoami` = root ] || exec sudo $0 $*

# on fait les vérifications pour gérer quand le conteneur se lancera
# sleep 70
# "/wait"

# on lance le script principal
python3 -u collect.py

