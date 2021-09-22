# import ssl
import sys
import json
import hashlib
import random
import string
import os
import time

import paho.mqtt.client
import paho.mqtt.publish

# Code exécuté par les clients(objets connectés) pour envoyer leurs informations par MQTT

# Static variables
MQTT_QOS = 2
MQTT_HOST = 'mosquittosrv'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASS = 'test'

MQTT_TOPIC_PREFIX = '/topic/'
MQTT_TOPIC_CAM = MQTT_TOPIC_PREFIX+'CAM'
MQTT_TOPIC_DENM = MQTT_TOPIC_PREFIX+'DENM'
MQTT_PAYLOAD_CAM = 'CAM MESSAGE DEFAULT CONTENT'
MQTT_PAYLOAD_DENM = 'DENM MESSAGE DEFAULT CONTENT'
MQTT_CLIENT_ID = 'client_1'
clientNumber = 0;

default_gps_in_zone = [1, 1]
default_gps_out_zone = [5, 5]
stationTypeList = [5, 10, 15]
causeList = [3, 4, 5, 6, 7]
subCauseList = [1, 2, 3, 4]

type_msg_random = [1, 2, 3, 4, 5] # 1(accident), 2(embouteillage), 3(inZone), 4(outZone), 5(random_msg)

# Fonctions de support
# Génère une chaine random alphanumeric d'une taille que l'on veut
def get_random_alphanum(this_size):
	return ''.join(random.choices(string.ascii_letters + string.digits, k=this_size))

def on_connect(client, userdata, flags, rc):
	print('connected')

# Formatte un message CAM au format JSON (Etat du véhicule)
	# stationId : N° immatricution (to md5 hash)
	# stationType : 5= véhicule ordinaire; 10= véhicule d'urgence ; 15 = véhiculeopérateurRoutier
	# vitesse (en klm/h) : 0 à 220
	# heading : 1 à 359
	# positions GPS : [lat, long] == [-90 à +90, -180 à +180] (map position)
def cam_payload(stationID, stationType, vitesse, head, gps):
	cam_data = {"stationID": stationID, "stationType": stationType, "vitesse": vitesse, "heading": head, "position": gps}
	return json.dumps(cam_data)
# Formatte un message DENM au format JSON (Evenements)
	# causecode : 3= travaux ; 4= accident; 5= Embouteillage;  6= route glissante;  7= brouillard;
def denm_payload(stationID, stationType, causeCode, subCauseCode, gps):
	denm_data = {"stationID": stationID, "stationType": stationType, "cause": causeCode, "subcause": subCauseCode, "position": gps}
	return json.dumps(denm_data)

# Publie un message MQTT
def publish_mqtt_msg(topic, msg, client_id):
	paho.mqtt.publish.single(
		topic= topic,
		payload= msg,
		qos= MQTT_QOS,	
		hostname= MQTT_HOST,
		port= MQTT_PORT,
		client_id= client_id,
		auth={
			'username': MQTT_USER,
			'password': MQTT_PASS
		}
	)

# CHOIX 1 : Publie 2 messages DENM pour faire remonter un messsage accident
def publish_mqtt_crash_messages():
	print("on envoie 2 messages MQTT qui seront couplés en un accident")
	stationID = get_random_alphanum(7) # stationID 1 aléatoire
	stationID2 = get_random_alphanum(7) # stationID 2 aléatoire
	stationType = random.choice(stationTypeList) # stationType aléatoire
	gps_position = [random.uniform(0.5, 2.5), random.uniform(0.6, 2.6)]
	cause = 4
	subCause = random.choice(subCauseList) # subCause aléatoire
	publish_mqtt_msg(
			MQTT_TOPIC_DENM,
			denm_payload(
				stationID,
				stationType, 
				str(cause), # cause code accident
				str(subCause), # random sub cause code
				str(gps_position) # same coord gps
				),
			stationID
		)
	print("DENM CRASH Message 1 sent")	
	time.sleep(1)
	publish_mqtt_msg(
			MQTT_TOPIC_DENM,
			denm_payload(
				stationID2,
				stationType, 
				str(cause), # cause code accident
				str(subCause), # sub cause code
				str(gps_position) # same coord gps
				),
			stationID2
		)	
	print("DENM CRASH Message 2 sent")
# CHOIX 2 : Publie 3 messages CAM pour faire remonter un embouteillage
def publish_mqtt_jam_messages():
	print("on envoie 3 messages CAM qui seront couplés en un embouteillage")
	stationID = get_random_alphanum(7) # stationID aléatoire
	stationID2 = get_random_alphanum(7) # stationID2 aléatoire
	stationID3 = get_random_alphanum(7) # stationID3 aléatoire
	stationType = random.choice(stationTypeList) # stationType aléatoire
	vitesse = 30
	gps_position = [random.uniform(0.5, 2.5), random.uniform(0.6, 2.6)]
 	#CAM
	if random.randint(0, 1) == 0:
		publish_mqtt_msg(
			MQTT_TOPIC_CAM, 
			cam_payload(
				stationID, 
				stationType, 
				str(vitesse), # vitesse
				str(random.randint(1, 359)), # angle
				str(gps_position) # same coord gps
				),
				stationID
		)
	print("CAM Jam Message 1 sent ")
	time.sleep(1)
	#CAM
	if random.randint(0, 1) == 0:
		publish_mqtt_msg(
			MQTT_TOPIC_CAM, 
			cam_payload(
				stationID2, 
				stationType, 
				str(vitesse), # vitesse
				str(random.randint(1, 359)), # angle
				str(gps_position) # same coord gps
				),
				stationID2
		)
	print("CAM Jam Message 2 sent ")
	time.sleep(1)
	#CAM
	if random.randint(0, 1) == 0:
		publish_mqtt_msg(
			MQTT_TOPIC_CAM, 
			cam_payload(
				stationID3, 
				stationType, 
				str(vitesse), # vitesse
				str(random.randint(1, 359)), # angle
				str(gps_position) # same coord gps
				),
				stationID3
		)
	print("CAM Jam Message 3 sent ")

# Publie un message inZone pour faire remonter un véhicule dans la zone
def publish_mqtt_inZone_message():
	print("on envoie un message CAM ou DENM dont la position sera incluses dans la zone")
	stationID = get_random_alphanum(7) # stationID aléatoire
	stationID2 = get_random_alphanum(7) # stationID aléatoire
	stationType = random.choice(stationTypeList) # stationType aléatoire
	cause = random.choice(causeList) # cause aléatoire
	subCause = random.choice(subCauseList) # subCause aléatoire
	default_gps_in_zone_random = [random.uniform(0.5, 1.5), random.uniform(0.5, 1.5)]
	publish_mqtt_msg(
			MQTT_TOPIC_CAM, 
			cam_payload(
				stationID, 
				stationType, 
				str(random.randint(5, 220)), # vitesse
				str(random.randint(1, 359)), # angle
				str(default_gps_in_zone_random) # coord gps inZone
				),
				stationID
		)
	print("CAM InZone Message sent")
	publish_mqtt_msg(
		MQTT_TOPIC_DENM,
		denm_payload(
			stationID2,
			stationType, 
			str(cause), # cause code
			str(subCause), # sub cause code
			str(default_gps_in_zone_random) # coord gps inZone
			),
		stationID2
	)
	print("DENM InZone Message sent")	
# Publie un message outZone pour faire remonter un véhicule en dehors la zone
def publish_mqtt_outZone_message():
	print("on envoie un message CAM ou DENM dont la position sera en dehors de la zone")
	stationID = get_random_alphanum(7) # stationID aléatoire
	stationID2 = get_random_alphanum(7) # stationID aléatoire
	stationType = random.choice(stationTypeList) # stationType aléatoire
	cause = random.choice(causeList) # cause aléatoire
	subCause = random.choice(subCauseList) # subCause aléatoire
	default_gps_out_zone_random = [random.uniform(1.2, 2.5), random.uniform(1.2, 2.5)]
	publish_mqtt_msg(
			MQTT_TOPIC_CAM, 
			cam_payload(
				stationID, 
				stationType, 
				str(random.randint(5, 220)), # vitesse
				str(random.randint(1, 359)), # angle
				str(default_gps_out_zone_random) # coord gps outZone
				),
				stationID
		)
	print("CAM OutZone Message sent")
	publish_mqtt_msg(
		MQTT_TOPIC_DENM,
		denm_payload(
			stationID2,
			stationType, 
			str(cause), # cause code
			str(subCause), # sub cause code
			str(default_gps_out_zone_random) # coord gps outZone
			),
		stationID2
	)
	print("DENM OutZone Message sent")	
# Choix 3 : Génère et publie un message inZone ou OutZone selon le choix de l'user
def publish_in_or_out_zone_message():
	try:
		value = int(input("InZone(1) ou OutZone(2):  "))
		if isinstance(value, int) == True and value == 1 :
			publish_mqtt_inZone_message()
		elif isinstance(value, int) == True and value == 2 :
			publish_mqtt_outZone_message()
		else :
			print("Choix incorrecte")
			sys.exit(0)	
	except:
		print("type error caught")

# Genère et publie un message CAM(0) ou DENM(1) avec des paramètres random
def publish_mqtt_random_message():
	print("génération et publication au hasard d'un message CAM(0) ou DENM(1) avec des valeurs random")
	stationID = get_random_alphanum(7) # stationID aléatoire
	stationType = random.choice(stationTypeList) # stationType aléatoire
	gps_position = [random.uniform(0.5, 2.5), random.uniform(0.6, 2.6)]
 	#CAM
	if random.randint(0, 1) == 0:
		publish_mqtt_msg(
			MQTT_TOPIC_CAM, 
			cam_payload(
				stationID, 
				stationType, 
				str(random.randint(5, 220)), # vitesse
				str(random.randint(1, 359)), # angle
				str(gps_position) # coord gps
				),
				stationID
		)
		print("CAM Message sent ")
	# DENM
	else : 
		cause = random.choice(causeList) # cause aléatoire
		subCause = random.choice(subCauseList) # subCause aléatoire
		publish_mqtt_msg(
			MQTT_TOPIC_DENM,
			denm_payload(
				stationID,
				stationType, 
				str(cause), # cause code
				str(subCause), # sub cause code
				str(gps_position) # coord gps
				),
			stationID
		)
		print("DENM Message sent")
# Genère et publie un message CAM avec les param de l'user
def gen_and_publish_spec_cam_msg():
	# on construit le payload
	try :
		stationID = input("Indiquer la stationID (ex: N° immatricution) :  ")
		stationType = int(input("Indiquer la stationType (5= véhicule ordinaire; 10= véhicule d'urgence ; 15 = véhiculeopérateurRoutier):  "))
		vitesse = int(input("Indiquer la vitesse :  "))
		head = int(input("Indiquer la head :  "))
		position_lat = float(input("Indiquer la position gps latitude:  "))
		position_long = float(input("Indiquer la position gps longitude:  "))
		gps=[position_lat, position_long]
	except ValueError:
		print("erreur de valeur, la construction du message CAM va être relancée ...")
		print("erreur = "+ValueError)
		gen_and_publish_spec_cam_msg()
	# on publie le message 
	publish_mqtt_msg(
			MQTT_TOPIC_CAM, 
			cam_payload(
				stationID, 
				stationType, 
				str(vitesse),
				str(head),
				str(gps)
				),
				stationID
		)
	print("Spec CAM Message sent ")
# Genère et publie un message DENM avec les param de l'user
def gen_and_publish_spec_denm_msg():
	# on construit le payload
	try :
		stationID = input("Indiquer la stationID (ex: N° immatricution) :  ")
		stationType = int(input("Indiquer la stationType (5= véhicule ordinaire; 10= véhicule d'urgence ; 15 = véhiculeopérateurRoutier):  "))
		causeCode = int(input("Indiquer le code de la cause (3= travaux ; 4= accident; 5= Embouteillage;  6= route glissante;  7= brouillard):  "))
		subCauseCode = 1
		position_lat = float(input("Indiquer la position gps latitude:  "))
		position_long = float(input("Indiquer la position gps longitude:  "))
		gps=[position_lat, position_long]
	except:
		print("erreur de valeur, la construction du message DENM va être relancée ...")
		gen_and_publish_spec_denm_msg()
	# on publie le message 
	publish_mqtt_msg(
			 MQTT_TOPIC_DENM,
			 denm_payload(
				 stationID,
				 stationType, 
				 str(causeCode), # cause code
				 str(subCauseCode), # sub cause code
				 str(gps)
				 ),
			stationID
		)
	print("Spec CAM Message sent ")

# CHOIX 4 : execute le choix de l'utilisateur pour générer et publier un nombre(choisi par l'user) de messages CAM ou DENM avec valeur random
def do_job_generate_and_publish_random_x_time():
	value = int(input("Indiquer le nombre de message à envoyer :  "))
	while value > 0 :
		print("Message N° "+str(value))
		publish_mqtt_random_message()
		value -= 1
# CHOIX 5 : execute le choix de l'utilisateur pour envoyer un/des message(s) CAM un nombre de fois choisie, avec les param de votre choix
def do_job_generate_and_publish_spec_cam_x_time():
	value = int(input("Indiquer le nombre de message à envoyer :  "))
	while value > 0 :
		print("Message N° "+str(value))
		gen_and_publish_spec_cam_msg()
		value -= 1
# CHOIX 6 : execute le choix de l'utilisateur pour envoyer un/des message(s) DENM un nombre de fois choisie, avec les param de votre choix
def do_job_generate_and_publish_spec_denm_x_time():
	value = int(input("Indiquer le nombre de message à envoyer :  "))
	while value > 0 :
		print("Message N° "+str(value))
		gen_and_publish_spec_denm_msg()
		value -= 1
# CHOIX 7 envoie un nombre random de message avec paramètres random de type random
def do_job_simulate_random():
	print("\n")
	print(">>>>>>>>>>>>>>>>>>>>>>>    <<<<<<<<<<<<<<<<<<<<<<<")
	print("> Plusieurs simulations random vont être lancées <")
	print(">>>>>>>>>>>>>>>>>>>>>>>    <<<<<<<<<<<<<<<<<<<<<<<")
	while True :
		# choisit un nombre de message à envoyer pour ce tour
		nb_msg = random.randint(2, 20)
		print("\n# Simulation lancé pour "+str(nb_msg)+" messages")
		for x in range(0, nb_msg) :
			# on tire un type de message aléatoirement
			print("\n#---- MESSAGE N° "+ str(x))
			type_msg = random.choice(type_msg_random)
			# on envoie ce type de message
			cases = {
				1: lambda: 
					#  1(accident), 
					publish_mqtt_crash_messages(),
				2: lambda: 
					# 2(embouteillage), 
					publish_mqtt_jam_messages(),
				3: lambda: 
					# 3(inZone), 
					publish_mqtt_inZone_message(),
				4: lambda: 
					# 4(outZone), 
					publish_mqtt_outZone_message(),
				5: lambda: 
					# 5(random_msg)
					publish_mqtt_random_message()
			}
			cases.get(type_msg, lambda: print("Aucun type de message correspondant"))()
			time.sleep(5)
		time.sleep(10)	
# CHOIX 8 : clean le terminal
def clean_term() :
	print(chr(27) + "[2J")
	os.system('cls' if os.name == 'nt' else 'clear')		
# execute le choix de l'utilisateur
def do_job_from_choice(value):
    cases = {
        1: lambda: 
			# 1 génère un accident
			publish_mqtt_crash_messages(),
        2: lambda: 
			# 2 génère un embouteillage
			publish_mqtt_jam_messages(),
        3: lambda: 
			# 3 Génère un message inZone ou OutZone
			publish_in_or_out_zone_message(),
        4: lambda: 
			# 4 envoie un/des message(s) CAM ou DENM random un nombre de fois choisie
			do_job_generate_and_publish_random_x_time(),
        5: lambda: 
			# 5 envoie un/des message(s) CAM un nombre de fois choisie, avec les param de votre choix
			do_job_generate_and_publish_spec_cam_x_time(),
		6: lambda: 
			# 6 envoie un/des message(s) DENM un nombre de fois choisie, avec les param de votre choix
			do_job_generate_and_publish_spec_denm_x_time(),
		7: lambda: 
			# 7 simulate
			do_job_simulate_random(),
		8: lambda: 
			# 8 clean_term
			clean_term(),	
    }
    cases.get(value, lambda: print("Aucun choix correspondant"))()
# # Traitement du MAIN (Simule les objets connectés qui envoient des données)
def run() :
	irestart = 0 
	value = 0
	while irestart == 0:

		# on montre les choix à l'user
		print("\nEnvoie de messages MQTT pour simuler un/des objet(s) connecté(s) :")
		print("1 envoie un message génère un accident")
		print("2 envoie un message génère un embouteillage")
		print("3 envoie un message Génère un message inZone ou OutZone")
		print("4 envoie un/des message(s) CAM ou DENM random un nombre de fois choisie")
		print("5 envoie un/des message(s) CAM un nombre de fois choisie, avec les param de votre choix")
		print("6 envoie un/des message(s) DENM un nombre de fois choisie, avec les param de votre choix")
		print("7 génère un nombre de message random avec paramètres random de type random à l'infini")
		print("8 clean le terminal")

		# on attend le choix de l'utilisateur 
		try:
			value = int(input("Entrer votre choix :  "))
		except:
			print("type error caught")
		finally :	
			if isinstance(value, int) == False or value < 1 or value > 8 :
				print("Choix incorrecte")
				sys.exit(0)

		# on applique le traitemnt du choix de l'user
		do_job_from_choice(value)

		# on lui demande s'il veut recommencer
		try:
			irestart = 1 # on marque le programme en arrêt par default
			irestart = int(input("On continue ? 0=yes / 1=no :  "))
		except:
			print("type error caught")
		finally:	
			if isinstance(irestart, int) == False or irestart < 0 or irestart > 1 :
				print("Choix incorrecte")

# MAIN
def main():
	while True :
		try :
			do_job_simulate_random()	
		except:
			e = sys.exc_info()[0]
			print("!!!!!!!!! main(), ERROR caught= "+str(e)) 	
		finally :
			print("retry in 5 sec ...")
			time.sleep(5)
if __name__ == '__main__':
	main()
	sys.exit(0)

# Unused
# Génére et publie un nombre(choisi par l'user) de messages CAM ou DENM par default 
def do_job_generate_and_publish_default_x_time():
		value = int(input("Indiquer le nombre de message à envoyer :  "))
		while value > 0 :
			print("Message N° "+str(value))
			publish_mqtt_random_default_message()
			value -= 1	
# Publie un message MQTT CAM par default
def publish_mqtt_default_CAM_message():
	print("publication d'un message MQTT CAM par default")
	paho.mqtt.publish.single(
			topic= MQTT_TOPIC_CAM,
			payload= MQTT_PAYLOAD_CAM,
			qos= MQTT_QOS,
			hostname= MQTT_HOST,
			port= MQTT_PORT,
			client_id= MQTT_CLIENT_ID,
			auth={
				'username': MQTT_USER,
				'password': MQTT_PASS
			}
		)
# Publie un message MQTT DENM par default
def publish_mqtt_default_DENM_message():

	print("publication d'un message MQTT DENM par default")
	paho.mqtt.publish.single(
			topic= MQTT_TOPIC_DENM,
			payload= MQTT_PAYLOAD_DENM,
			qos= MQTT_QOS,
			hostname= MQTT_HOST,
			port= MQTT_PORT,
			client_id= MQTT_CLIENT_ID,
			auth={
				'username': MQTT_USER,
				'password': MQTT_PASS
			}
		)
# Publie au hasard un message CAM(0) ou DENM(1) par default
def publish_mqtt_random_default_message():
	print("publication au hasard d'un message CAM(0) ou DENM(1) par default")
 	#CAM
	if random.randint(0, 1) == 0:
		publish_mqtt_default_CAM_message()
		print("CAM Message sent ")
	# DENM
	else : 
		publish_mqtt_default_DENM_message()
		print("DENM Message sent")
