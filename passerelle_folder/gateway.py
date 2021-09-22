#import ssl
import sys
import json
import math
import logging
import time
from datetime import datetime

import paho.mqtt.client
import xmpp

# Code exécuté sur la passerelle pour 
# - analyser les msg recues des objets connectés
# - relayer les msg MQTT en XMPP au collecteur

# Static variables MQTT
MQTT_QOS = 2
MQTT_HOST = 'mosquittosrv'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASS = 'test'

MQTT_TOPIC = '/topic/#'
MQTT_CLIENT_ID = 'client_2'
MQTT_CLEAN_SESSION = False

GPS_ZONE = [1, 1] #coord gps de la zone à vérifier
DICT_ACCIDENT_ZONE = dict() # Dictionnaire de (String, String) : #key stationID_First - #Value msg_content_json
DICT_EMBOUTEILLAGE = dict() # Dictionnaire de (string, String) : #key stationID_First - #Value msg_content_json / taille 3 max

# STATIC VARIABLE XMPP
XMPP_HOST = 'prosodysrv'

# THIS CLIENT 
FROM_CLIENT_JID = "user_gate@localhost"
CLIENT_PASSWORD = "test"
AUTHORIZED_JIDS = ["admin@localhost"]

# FORWARD TO CLIENT
TO_CLIENT_JID = "user_col@localhost"
CLIENT_PASSWORD = "test"
AUTHORIZED_JIDS = ["admin@localhost"]

# RESS
RESS_ACCIDENT = "/accident"
RESS_JAM = "/bouchon"
RESS_ZONEIN = "/zonein"
RESS_ZONEOUT = "/zoneout"

# s'abonne à un topic
def on_connect(client, userdata, flags, rc):
	print('############# CLIENT INFO ###############' + str(datetime.now()))
	print('connected (%s)' % client._client_id)
	print('\tuserdata (%s)' % userdata)
	print('\tflags (%s)' % flags)
	print('\trc (%s)' % rc)
	print('#########################################')
	client.subscribe(topic=MQTT_TOPIC, qos=2)

# Envoie les données d'un message recue à l'unité de traitement
def on_message(client, userdata, message):
	print('\n############# MSG INFO #####################################' + str(datetime.now()))
	print('------------------------------')
	print('userdata: %s' % userdata)
	print('client: %s' % client)
	print('topic: %s' % message.topic)
	print('payload: %s' % message.payload)
	print('qos: %d' % message.qos)
	print('#############################################################\n')

	# Envoie au traitement
	msg_content_json = getJSONObject(message.payload)
	if isinstance(msg_content_json, dict):
		send_to_treatments(str(message.topic), client, msg_content_json)
	else :
		print("ceci était un message de test ( type= <class 'bytes'> ), on ne va pas plus loin")	

# Renvoie un objet JSON depuis un string
def getJSONObject(message_payload):
	try :
		return json.loads(message_payload)
	except:
		print("le message n'est pas un string JSON exploitable")

# Envoie le message au traitement adéquate
def send_to_treatments(topic, client, msg_content_json):
	if topic == '/topic/CAM' :
		# TRAITEMENT 1, 2, 4
		print("> le message est envoyé au traitement 1")
		check_in_zone(client, msg_content_json)
		print("> le message est envoyé au traitement 2")
		check_out_zone(client, msg_content_json)
		print("> le message est envoyé au traitement 4")
		check_traffic_jam(client, msg_content_json)
	elif topic == '/topic/DENM' :
		# TRAITEMENT 3
		print("> le message est envoyé au traitement 3")
		check_cause(client, msg_content_json)
	else  :
		print(">le message(ni CAM, ni DENM) n'est pas issue d'un topic traité par la passerelle ") 	
	
# TRAITEMENT 1 - Vérifie si un véhicule entre dans la zone (GPS_ZONE)
def check_in_zone(client, msg_content_json) :
	try:
		print('check_in_zone() : vérifie si le véhicule entre dans la zone')
		if is_position_in_zone(GPS_ZONE, list(msg_content_json['position'].split(","))) == True:
			print(">> le véhicule est proche de l'entrée de la zone, on envoie un msg XMPP au collecteur")
			send_xmpp_message('zonein', msg_content_json)
		else :
			print("le véhicule n'est pas dans la zone")	
	except ValueError:
		print("check_in_zone error catch "+ str(ValueError))	
# Compare si une position GPS est proche de l'entrée d'une zone
	# on simule une vérification (différent à moins de 5 dixième près) 
	# sinon marker & polygon à utiliser pour implémenter Google Map
def is_position_in_zone(zone, pos):
	pos_lat = float( (pos[0])[1:] )
	pos_long = float( (pos[1])[0:-1] )
	diff_lat_post_lat = abs(float(float(zone[0]) - pos_lat))
	diff_long_post_long = abs(float(float(zone[1]) - pos_long))
	if diff_lat_post_lat < 1.1 and diff_long_post_long < 1.1:
		return True
	else :
		return False

# TRAITEMENT 2 - Vérifie si un véhicule sort de la zone (GPS_ZONE)
def check_out_zone(client, msg_content_json) :
	try:
		print('check_out_zone() : vérifie si le véhicule est en dehors de la zone')
		if is_position_out_zone(GPS_ZONE, list(msg_content_json['position'].split(","))) == True:
			print(">> le véhicule est en dehors de la zone, on envoie un msg XMPP au collecteur")
			send_xmpp_message('zoneout', msg_content_json)
		else :
			print("le véhicule n'est pas en dehors de la zone")	
	except ValueError:
		print("check_out_zone error catch "+ str(ValueError))	
# Compare si une position GPS est en dehors d'une zone
	# on simule une vérification (différent à moins de 2 au dixième près) 
	# sinon marker & polygon à utiliser pour implémenter Google Map
	print("is_position_out_zone() called")
def is_position_out_zone(zone, pos):
	pos_lat = float( (pos[0])[1:] )
	pos_long = float( (pos[1])[0:-1] )
	diff_lat_post_lat = abs(float(float(zone[0]) - pos_lat))
	diff_long_post_long = abs(float(float(zone[1]) - pos_long))
	if  diff_lat_post_lat > 1.1 or diff_long_post_long > 1.1:
		print("TRUE est en dehors")
		return True
	else :
		print("FALSE n'est pas en dehors")
		return False

# Traitement 3 - Vérification de la cause
def check_cause(client, msg_content_json):
		if msg_content_json['cause'] == "3" :
			print("message avec cause travaux")
			print("on n'envoie pas au collecteur")
		elif msg_content_json['cause'] == "4" :	
			print("message avec cause accident")
			check_accident(client, msg_content_json)
		elif msg_content_json['cause'] == "5" :
			print("message avec cause Embouteillage")
			print("on n'envoie pas au collecteur")
		elif msg_content_json['cause'] == "6" :
			print("message avec cause route glissante")
			print("on n'envoie pas au collecteur")
		elif msg_content_json['cause'] == "7" :
			print("message avec cause brouillard")
			print("on n'envoie pas au collecteur")
		else :
			print("il n'y a aucune cause correspondant à ce code")		
# TRAITEMENT pour cause accident
	# Si l’événement est remonté par au moins 2 véhicules
	# - 2 véhicules dont la stationID est différent
	# - 2 véhicule qui sont à la même position
def check_accident(client, msg_content_json) :
	print('check_accident() function')
	isEntryNeedDelete = False
	keyToDelete = ""
	isEntryNeedInsert = False

	print("Dictionnaire des véhicules enregistrés: \n"+print_dic(DICT_ACCIDENT_ZONE, False)+"\n")

	# on vérifie que le dictionnaire contient une entrée
	if len(DICT_ACCIDENT_ZONE) > 0 :
		# on vérifie si la même stationID à déjà signalé un accident dans la zone
		if check_if_key_exist(DICT_ACCIDENT_ZONE,msg_content_json['stationID']) :
			print("la station a déjà signalé un accident")
		else :	
			# Pour chaque véhicule ayant déclaré un accident 
			for key in DICT_ACCIDENT_ZONE:
				# on vérifie si sa position serait près de la position du véhicule courant
					# if is_position_near_position(DICT_ACCIDENT_ZONE[key], msg_content_json):: 
				# on récupère les 2 stations ID
				stationID_Dict = key
				stationID_Current = msg_content_json['stationID']
				# leur position lors de l'accident à récupérer dans le tableau des messages CAM
				# position_Dict = DICT_ACCIDENT_ZONE[key]
				# position_current = msg_content_json
				# on envoie un message XMPP au collecteur avec ces informations
				print(">> un accident va être signalé par message XMPP au collecteur")
				print("stationID_Dict= "+stationID_Dict)
				print("stationID_Current= "+stationID_Current)
				data = [DICT_ACCIDENT_ZONE[stationID_Dict], msg_content_json]
				send_xmpp_message('accident', data)
				# on marque cette entrée du dictionnaire en suppression  
				print("véhicule du dico marqué pour suppression")
				isEntryNeedDelete = True
				keyToDelete = key
	else :
		print("aucun véhicule n'est en attente pour un accident")
		# on marque le nouveau tuple en insertion
		isEntryNeedInsert = True
	
	# on vérifie si une entrée est à supprimer	
	if isEntryNeedDelete == True :
		# on supprime cette entrée du dictionnaire 
		delete_entry_from_dic(keyToDelete, 0, True) 
		print("\n############## stationID supprimées des accidents en attente #")
		print("Dictionnaire des véhicules enregistrés: \n"+print_dic(DICT_ACCIDENT_ZONE, False)+"\n")

	# on vérifie si une entrée est à insérer
	if isEntryNeedInsert == True :
		# on insère dans le dictionnaire le nouveau tuple
		insert_entry_from_dic(msg_content_json['stationID'], msg_content_json, 0, True)
		print("\n############## stationID enregistrée dans les accidents en attente #")
		print("Dictionnaire des véhicules enregistrés: \n"+print_dic(DICT_ACCIDENT_ZONE, False)+"\n")	

# insert une entrée dans un dictionnaire (0 dic_accident, 1 dic_embouteillage)
def insert_entry_from_dic(key, value, num_dic, wantDisplay):
	# print("insert_entry_from_dic() called with key "+ str(key) + "value= "+ str(value))
	if num_dic == 0 :
		DICT_ACCIDENT_ZONE[key] = value
		if wantDisplay == True:
			print("Dictionnaire des véhicules enregistrés:")	
			print_dic(DICT_ACCIDENT_ZONE, True)
	else :
		DICT_EMBOUTEILLAGE[key]	= value
		if wantDisplay == True:
			print("Dictionnaire des véhicules en embouteillage: \n")	
			print_dic(DICT_EMBOUTEILLAGE, True)		
# supprime une entrée dans un dictionnaire (0 dic_accident, 1 dic_embouteillage)
def delete_entry_from_dic(key, num_dic, wantDisplay):
	# print("delete_entry_from_dic() called with key= "+ str(key))
	if num_dic == 0 :
		del DICT_ACCIDENT_ZONE[key]
		if wantDisplay == True:
			print("Dictionnaire des véhicules enregistrés: \n")	
			print_dic(DICT_ACCIDENT_ZONE, True)
	else :
		del DICT_EMBOUTEILLAGE[key]	
		if wantDisplay == True:
			print("Dictionnaire des véhicules en embouteillage: \n")	
			print_dic(DICT_EMBOUTEILLAGE, True)

# TRAITEMENT 4 - Vérifie si il y a embouteillage
	# Au moins 3 véhicules roulent en dessous de la vitesse autorisée (ici 90km/h)
	# on devrait prendre des véhicules dans la même zone
	# on vérifie si la vitesse est en dessous 90
def check_traffic_jam(client, msg_content_json) :
	print('check_traffic_jam() function')
	if int(msg_content_json['vitesse']) < 90 :
		# si le dictionnaire à déjà 2 entrée et que la stationID n'est pas déjà enregistrée
		if len(DICT_EMBOUTEILLAGE) == 3 and not check_if_key_exist(DICT_EMBOUTEILLAGE, msg_content_json['stationID']):
			data_list = list()
			# on récupère l'ensemble des données des 3 véhicules
			for key in DICT_EMBOUTEILLAGE:
				data_list.append(DICT_EMBOUTEILLAGE[key])
			# on envoie un message XMPP avec les données récupérées pour signaler l'embouteillage
			print(">> il y a un embouteillage, on envoie un msg XMPP au collecteur")
			send_xmpp_message('bouchon', data_list)
			# on supprime tous les véhicules du DICT_EMBOUTEILLAGE
			DICT_EMBOUTEILLAGE.clear()
		else :
			print('il n\'y a pas assez de véhicule pour signaler un embouteillage')
			print('> le véhicule a été enregistré pour détection d\'embouteillage')	
			DICT_EMBOUTEILLAGE[msg_content_json['stationID']] = msg_content_json
			print("Dictionnaire des véhicules enregistrés: \n"+print_dic(DICT_EMBOUTEILLAGE, False)+"\n")
	else :
		print("> le véhicule ne présage pas d'embouteillage")	
# Vérifie si une key n'existe déjà pas dans un dictionnaire 
def check_if_key_exist(dic, stationID) :
	isStationIDExist = False
	for key in dic:
		if key == stationID :
			isStationIDExist = True
			break
	return isStationIDExist		
# Affiche le contenu d'un dictionnaire 
def print_dic(dic, wantDisplay):
	dic_str = ""
	for x in dic:
		if wantDisplay : 
			print(x +" -> "+ str(dic[x]))
		dic_str += x +" -> "+ str(dic[x]) + " \n"
	return dic_str	
# Vérifie si une position du dictionnarie d'accident est proche de la position courante
def is_position_near_position(msg_content_json_dict, msg_content_json) :
	print('is_position_near_position() : vérifie si le véhicule est dans la même zone qu\'un autre')
	try:
		# on formatte la position ddu véhicule du dic
		pos_lat_dic = float( (list(msg_content_json_dict['position'].split(",")) [0])[1:] ) 
		pos_long_dic = float( (list(msg_content_json_dict['position'].split(",")) [1])[0:-1] )
		# on formatte la position du véhicule courant
		pos_lat_current = float( (list(msg_content_json['position'].split(",")) [0])[1:] )
		pos_long_current = float( (list(msg_content_json['position'].split(",")) [1])[0:-1] )

		if pos_lat_dic - pos_lat_current < abs(0.2) and pos_long_dic - pos_long_current < abs(0.2):
			print("le véhicule est près de l'autre, il y a donc accident")
			return True
		else :
			print("le véhicule n'est pas près de l'autre")
			return False
	except ValueError:
		print("check_in_zone error catch "+ str(ValueError))	

# Envoie un message XMPP au jabber_id spécifié
# type : 1-> entre dans la zone | 2 -> sort de la zone | 3 -> accident | 4 -> embouteillage 
def send_xmpp_message(type, data) :
	type_str = ("entre dans la zone", ("sort de la zone", ("accident", "embouteillage")[type == 3])[type == 2])[type == 1]
	print("xmpp message sent, type= "+type_str+" data= "+str(data))
	
	# Initialize the client.
	jid = xmpp.JID(FROM_CLIENT_JID)
	client = xmpp.Client(jid.domain,debug=[]) # debug off
	# client = xmpp.Client(jid.domain,debug=['always']) # debug on

	if not client.connect(server=(XMPP_HOST, 5222), proxy=None, secure=None, use_srv=0):
		print("le client n'as pas pu se connecter au serveur")
		return
	else: 
		print("## XMPP : client.connect est connecté")    

	# Authenticate the client.
    # sasl=1 ou 0 Simple Authentication and Security Layer (ne change rien au connect ni à l'auth =) )
	if not client.auth(jid.node, CLIENT_PASSWORD, jid.resource, sasl=0):
    # if not client.auth(jid.node, client_password, jid.resource):
		print("le client n'as pas pu s'authentifier au serveur au node ")
		print("jid.node= "+jid.node)
		print("client_password= "+CLIENT_PASSWORD)
		print("jid.resource= "+jid.resource)
		return
	else:
		print("## XMPP : client.auth est authentifié")   

	client.sendInitPresence()
	client.Process()

	# envoie du message XMPP
	if(type == 'accident') :
		client.send(xmpp.protocol.Message(TO_CLIENT_JID+RESS_ACCIDENT, json.dumps(data)))
	elif(type== 'bouchon'):
		client.send(xmpp.protocol.Message(TO_CLIENT_JID+RESS_JAM, json.dumps(data)))
	elif(type=='zonein'):
		client.send(xmpp.protocol.Message(TO_CLIENT_JID+RESS_ZONEIN, json.dumps(data)))
	elif(type=='zoneout'):
		client.send(xmpp.protocol.Message(TO_CLIENT_JID+RESS_ZONEOUT, json.dumps(data)))
	else :
		print("on ne fait pas suivre le message")	
    
# Traitement du MAIN (recoit les messages des objets connectés)
def run() :
	# On loop la connexion tant que mosquitto injoignable
	# Reconnexion si erreur aussi
	while True :
		print("Connexion au srv MQTT en cours ...")
		try :
			client = paho.mqtt.client.Client(client_id=MQTT_CLIENT_ID, clean_session=MQTT_CLEAN_SESSION)
			client.username_pw_set(MQTT_USER, MQTT_PASS)
			client.on_connect = on_connect
			client.on_message = on_message
			# client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pem', tls_version=ssl.PROTOCOL_TLSv1_2)
			client.connect(host=MQTT_HOST, port=MQTT_PORT)
			client.loop_forever()
		except:
			e = sys.exc_info()[0]
			print("!!!!!!!!! run(), ERROR caught= "+str(e))
		finally :
			print("retry in 5 sec ...")
			time.sleep(5)	 

# MAIN
def main():
	run()

if __name__ == '__main__':
	main()
	sys.exit(0)
