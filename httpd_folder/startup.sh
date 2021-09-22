#!/bin/bash

# on relance le script en root
#[ `whoami` = root ] || exec sudo $0 $*

# on fait les vérifications pour gérer quand le conteneur se lancera
# "/wait"

# on lance le script principale
docker-php-entrypoint apache2-foreground

