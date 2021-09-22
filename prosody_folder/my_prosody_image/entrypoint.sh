#!/bin/bash
set -e
set -x

# on fait les vérifications pour gérer quand le conteneur se lancera
# "/wait"

# si l'user ID de l'utilisateur est celui de prosody
if [[ $(id -u) -eq $(id -u prosody) ]]; then
    if [[ -z $(ls -A /etc/prosody | head -1) ]] ; then
        cp -Rv /etc/prosody.default/* /etc/prosody/
    fi
    # configuration du domaine selon la valeur d'environnement passée
    if [[ -n $DOMAIN ]]; then
        sed -i "s/example.com/$DOMAIN/g" /etc/prosody/prosody.cfg.lua
        sed -i 's/enabled = false -- Remove this line to enable/enabled = true -- false to disable/' /etc/prosody/prosody.cfg.lua
        # Copie des clé SSH de localhost si inexistante
        if [[ ! -f /etc/prosody/certs/$DOMAIN.key && -f /etc/prosody/certs/localhost.key ]]; then
             cp /etc/prosody/certs/localhost.key /etc/prosody/certs/$DOMAIN.key
        fi
        if [[ ! -f /etc/prosody/certs/$DOMAIN.crt && -f /etc/prosody/certs/localhost.crt ]]; then
            cp /etc/prosody/certs/localhost.crt /etc/prosody/certs/$DOMAIN.crt
        fi
    fi
    # MAJ des modules
    if [ -z $(ls -A ${PROSODY_MODULES} | head -1) ]; then
        /usr/bin/update-modules
    fi
    # Création des utilisateurs
    if [[ $1 == "prosody" && -n $LOCAL &&  -n $PASSWORD && -n $DOMAIN ]]; then
        prosodyctl register $LOCAL $DOMAIN $PASSWORD
    	prosodyctl register "user_gate" $DOMAIN $PASSWORD
    	prosodyctl register "user_col" $DOMAIN $PASSWORD
    	prosodyctl register "user_apache" $DOMAIN $PASSWORD
    	prosodyctl register "user_db" $DOMAIN $PASSWORD
    fi
else
   echo "l'user ID ne correspond pas !"
fi

# on lance le serveur
exec "$@"