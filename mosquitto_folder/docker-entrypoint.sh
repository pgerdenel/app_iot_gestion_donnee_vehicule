#!/bin/ash
set -e

echo "on lance les check avant de lancer le container"
# on fait les vérifications pour gérer quand le conteneur se lancera
# sleep 80
# "/wait"

# On set les permissions utilisateurs
user="$(id -u)"
if [ "$user" = '0' ]; then
	[ -d "/mosquitto" ] && chown -R mosquitto:mosquitto /mosquitto || false # true pour le debug
fi

exec "$@"
