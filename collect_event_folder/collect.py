import os
import time
import traceback
import xmpp
import sys
import mysql.connector 
import json 
import string 
import math
from decimal import Decimal
from datetime import datetime

# STATIC VARIABLE MYSQL
HOST = "mysqldb"
USER_DB = "rootrm"
PWD_DB = "test"
DB_NAME = "proso"

# STATIC VARIABLE XMPP
XMPP_HOST = 'prosodysrv'

# THIS CLIENT 
FROM_CLIENT_JID = "user_col@localhost"
CLIENT_PASSWORD = "test"
AUTHORIZED_JIDS = ["admin@localhost"]

# FORWARD TO CLIENT
TO_CLIENT_JID = "user_apache@localhost"
TO_CLIENT_ACCIDENT = "/accident"
TO_CLIENT_JAM = "/bouchon"
TO_CLIENT_ZIN = "/zonein"
TO_CLIENT_ZOUT = "/zoneout"
CLIENT_PASSWORD = "test"
AUTHORIZED_JIDS = ["admin@localhost"]

# recuperer valeur entre 2 autres depuis le début
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
# recuperer valeur entre 2 autres depuis la fin
def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

# on insert un message accident
def py_insert_accident(conn, pval) :
    print("> ENREGISTREMENT ACCIDENT EN BDD ...")
    try :
        # on enregistre l'accident'
        sql = "INSERT INTO accident (station_id_first, station_id_last) VALUES (%s, %s)"
        val = (pval[0]['stationID'] , pval[1]['stationID'])
        conn.cursor().execute(sql, val)
        conn.commit()
        print(conn.cursor().rowcount, "record accident inserted.")   
    except Exception:
        print("py_insert_accident "+str(Exception))
# on insert un message embouteillage
def py_insert_embouteillage(conn, pval) :
    print("> ENREGISTREMENT BOUCHON EN BDD ...")

    # on calcule la vitesse moyenne
    vitm = str( math.trunc((int(pval[0]['vitesse']) + int(pval[1]['vitesse']) + int(pval[2]['vitesse'])) / 3))
    print("vit_moy= "+vitm)

    try :
        # on enregistre l'embouteillage'
        sql = "INSERT INTO embouteillage (station_id_first, station_id_second, station_id_last, vitesse_moyenne) VALUES (%s, %s, %s, %s)"
        val = (pval[0]['stationID'] , pval[1]['stationID'], pval[2]['stationID'], vitm)
        conn.cursor().execute(sql, val)
        conn.commit()
        print(conn.cursor().rowcount, "record embouteillage inserted.") 
    except Exception:
        print("py_insert_embouteillage "+str(Exception))
# on insert un message zonein
def py_insert_zonein(conn, pval) :
    print("> ENREGISTREMENT ZONEIN EN BDD ...")
    try :
        # on enregistre l'zonein'
        sql = "INSERT INTO zonein (zone_lat, zone_long) VALUES (%s, %s)"
        
        position_lat = str(find_between(pval['position'], "[", ","))
        position_long = str(find_between(pval['position'], ",", "]"))
        print("position lat "+position_lat)
        print("position long"+position_long)

        val = (position_lat , position_long)

        conn.cursor().execute(sql, val)
        conn.commit()        
        print(conn.cursor().rowcount, "record zonein inserted.")  
    except Exception:
        print("py_insert_zonein "+str(Exception))
# on insert un message zoneout
def py_insert_zoneout(conn, pval) :
    print("> ENREGISTREMENT ZONEOUT EN BDD ...")
    try :
        # on enregistre l'zoneout'
        sql = "INSERT INTO zoneout (zone_lat, zone_long) VALUES (%s, %s)"

        position_lat = str(find_between(pval['position'], "[", ","))
        position_long = str(find_between(pval['position'], ",", "]"))
        print("position lat "+position_lat)
        print("position long"+position_long)

        val = (position_lat , position_long)
        
        conn.cursor().execute(sql, val)
        conn.commit()
        print(conn.cursor().rowcount, "record zoneout inserted.")  
    except Exception:
        print("py_insert_zoneout "+str(Exception))

# permet de gérer les traitements liés à la reception d'un message
def handle_messages(jids):
    def handler(client, stanza):
        # on récupère les informations du message
        # on affiche les informations du message
        print("\n################ Nouveau message recu ###############"+ str(datetime.now()))
        msg_content =  str(stanza.getBody())
        sender = str(stanza.getFrom().getStripped()) # ex: user_apache@localhost
        sender2 = str(stanza.getFrom()) # ex: user_apache@localhost/accident
        receiver = str(stanza.getTo()) # ex: user_col@localhost/accident
        print("sender = " + sender)
        print("sender2 = " + sender2)
        print("receiver = " + receiver)
        print("content : " + msg_content)
        print("#####################################################") 
        # time.sleep(1) # le temps de voir le log message recue
        
        # initialisation de la connexion à la DB
        conn = mysql.connector.connect(host=HOST,user=USER_DB,password=PWD_DB, database=DB_NAME)

        # on récupère le type de message (accident ou bouchon)
        if receiver.find("accident") != -1 :
            print("> TYPE: ACCIDENT")

            # on décode le json du msg_content
            # msg_content =  msg_content=str.replace("\'", "\"")
            accident_json_object = json.loads(msg_content)

            # on le fait passer au serveur apache avec bosh en /accident
            client.send(xmpp.protocol.Message(TO_CLIENT_JID+TO_CLIENT_ACCIDENT, str(msg_content)))
            print("> message transmis au collecteur")

            # on enregistre l'évènement en BDD 
            py_insert_accident(conn, accident_json_object)
        elif receiver.find("bouchon") != -1 :
            print("> TYPE: BOUCHON RECUE")
            
            # on décode le json du msq_content
            # msg_content =  msg_content=str.replace("\'", "\"")
            bouchon_json_object = json.loads(msg_content)

            # on le fait passer au serveur apache avec bosh en /bouchon
            client.send(xmpp.protocol.Message(TO_CLIENT_JID+TO_CLIENT_JAM, str(msg_content)))
            print("> message transmis au collecteur")
            
            # on enregistre l'évènement en BDD 
            py_insert_embouteillage(conn, bouchon_json_object)
        elif receiver.find("zonein") != -1 :
            print("> TYPE: ZONEIN RECUE")

            # on décode le json du msq_content
            # msg_content =  msg_content=str.replace("\'", "\"")
            zonein_json_object = json.loads(msg_content)

            # on le fait passer au serveur apache avec bosh en /bouchon
            client.send(xmpp.protocol.Message(TO_CLIENT_JID+TO_CLIENT_ZIN, str(msg_content)))
            print("> message transmis au collecteur")
            
            # on enregistre l'évènement en BDD 
            py_insert_zonein(conn, zonein_json_object)
        elif receiver.find("zoneout") != -1 :
            print("> TYPE: ZONEOUT RECUE")

            # on décode le json du msq_content
            # msg_content =  msg_content=str.replace("\'", "\"")
            zoneout_json_object = json.loads(msg_content)
            
            # on le fait passer au serveur apache avec bosh en /bouchon
            client.send(xmpp.protocol.Message(TO_CLIENT_JID+TO_CLIENT_ZOUT, str(msg_content)))
            print("> message transmis au collecteur")

            # on enregistre l'évènement en BDD 
            py_insert_zoneout(conn, zoneout_json_object)
        else :
            print("ceci est un message de test")
            print("> TYPE: TEST RECUE")
            # on renvoie un accusé de reception à l'expéditeur
            client.send(xmpp.protocol.Message(sender, "message bien recue"))

            # on enregistre rien en BDD    
            print("> rien ne sera enregistré en BDD")

        conn.close()  
    return handler

# permet de gérer la xmpp presence au besoin
def handle_presences(jids):
    def handler(client, stanza):
        sender = stanza.getFrom()
        presence_type = stanza.getType()
        if presence_type == "subscribe":
            if any([sender.bareMatch(x) for x in jids]):
                client.send(xmpp.Presence(to=sender, typ="subscribed"))
    return handler
# client permettant de recevoir les messages & log en loop
def run_client(client_jid, client_password, authorized_jids):
    
    # Initialization du client
    jid = xmpp.JID(client_jid)
    # client = xmpp.Client(jid.domain,debug=['always']) # debug on
    client = xmpp.Client(jid.domain,debug=[]) # debug off

    # srv_true If you want to force SSL start (i.e. if port 5223 or 443 is remapped to some non-standard port) then set it to 1. If you want to disable tls/ssl support completely, set it to 0.
    if not client.connect(server=(XMPP_HOST, 5222), proxy=None, secure=None, use_srv=0):
        print("le client n'as pas pu se connecter au serveur")
        return
    else : 
        print("## XMPP : client.connect est connecté")    

    # Authentification
    # sasl=1 ou 0 Simple Authentication and Security Layer (ne change rien au connect ni à l'auth =) )
    if not client.auth(jid.node, client_password, jid.resource, sasl=0):
        print("le client n'as pas pu s'authentifier au serveur au node ")
        print("jid.node= "+jid.node)
        print("client_password= "+client_password)
        print("jid.resource= "+jid.resource)
        return
    else : 
        print("## XMPP : client.auth est authentifié")    

    # MESSAGE HANDLER
    message_callback = handle_messages(authorized_jids)
    client.RegisterHandler("message", message_callback)

    # PRESENCE HANDLER (Avertir si connecté ou pas)
    presence_callback = handle_presences(authorized_jids)
    client.RegisterHandler("presence", presence_callback)

    client.sendInitPresence()
    client.Process()

    # on loop à l'infini 
    while client.isConnected():
        client.Process()
        time.sleep(1)

# MAIN Traitement
def run() :
    # On loop la connexion si injoignable tant que prosody injoignable
	# Reconnexion si erreur aussi
    while True:
        print("Connexion au serveur XMPP en cours ...")
        try:    
            # conn = mysql.connector.connect(host=HOST,user=USER_DB,password=PWD_DB, database=DB_NAME)
            # test_connect(conn)
            run_client(FROM_CLIENT_JID, CLIENT_PASSWORD, AUTHORIZED_JIDS)
        except:
            e = sys.exc_info()[0]
            print("run() Erreur = "+str(e))
            # traceback.print_exc()
        print("reconnexion en cours ...")
        time.sleep(10)

if __name__ == "__main__":
    run()

# test la connexion à la db
def test_connect(conn) :
    cursor = conn.cursor()
    print("#############################") 
    print("connexion BDD ok !")
    conn.close()

