# Développement et conteneurisation d’une architecture permettant la gestion de données issues de véhicules

__Introduction__

Nous développerons une solution permettant de récupérer, analyser et signaler des messages routiers 
issues d’objets connectées tel que des automobilistes. Nous mettrons en pratique les différentes 
données, protocoles et serveurs définis dans l’architecture globale. 

Le comportement d’objets connectées sera simulés par un programme qui émet des messages. 
Le messages MQTT  émis par les objets connectés seront échangés avec le serveur MQTT Mosquitto, 
tandis que les messages XMPP seront échangés grace au serveur XMPP Prosody.
Les informations remontées pour ce projet (accident et bouchons) seront disponibles depuis le serveur 
web Apache et ils seront sauvegardées dans une base de données MySQL.

L’ensemble de ces intéractions se fera entre plusieurs entités intermédiaires qui assureront les 
fonctionnalitées et la communication entre les différents serveurs. 

Nous utiliserons la virtualisation afin de partitionner chacune de ses entitées et de pouvoir gérer leur 
ressources.

__Technologies utilisées __

__Python :__ 
- simulation des objets connectés
- communication MQTT avec la librairie paho-mqtt
- logique de traitement des messages
- communication XMPP avec la librairie xmpppy

__Javascript :__
- reception des messages XMPP sur Apache avec la librairie Strophe.js gràçe au protocole BOSH

__HTML & CSS :__
- mise en forme du contenu des messages recues

__Mosquitto :__
- communication MQTT
- publish/subscribe
 
__Prosody :__
- B   osh    (XMPP over HTTP)
- sauvegarde des données en BDD

__Apache :__
- mod_proxy
- mod_rewrite
- virtualhost
- API    Rest    d’accès aux données stockées en BDD
 
__MySQL :__
- stockage et archivage des évènements
- stockage des utilisateurs Pr   osody   
- stockage des échanges XMPP

__Docker :__
- conteneurisation des différentes entitées
- communication des différentes entitées
- déploiement avec docker-compose

__Modésalition rapide__

![image](https://user-images.githubusercontent.com/47711469/134272009-5ddb0e19-a102-4fa6-a12c-4d70f295f619.png)


__Architecture__

L’ensemble des serveurs ont été conteneurisés avec docker.

L’ensemble des traitements intermédiaires ont été intégré dans des programmes python eux même 
conteneurisés avec docker.

Le client MQTT publie des messages MQTT gràçe à paho-mqtt à la passerelle, par l’intermédiaire du 
serveur MQTT Eclipse-Mosquitto.

La passerelle est abonnée aux topics MQTT de Mosquitto. Elle receptionne et analyse les messages, 
puis transmet des évènements de type ‘accident’, ‘embouteillage’, ‘entrée de zone’, ‘sortie de zone’ 
avec le protocole XMPP à destination du collecteur d’évènements, par l’intermédiaire du serveur 
XMPP Prosody.

Le collecteur d’évènement enregistre ces évènements en base de donnée MySQL. Il met à disposition 
également les données de ces messages pour le serveur apache qui les recoit gràçe au protocole 
BOSH(XMPP over HTTP).

Le serveur XMPP Prosody assure donc les communications XMPP et BOSH entre les acteurs, permet 
de les authentifier, de pointer sur des ressources(accident et bouchon).

Il enregistre également les utilisateurs et tous leur message en base de donnée MySQL.

Le serveur Web apache met à disposition une application web permet de voir en temps réeel les 
évènements remontés par le collecteur mais également l’historique de ces évènements. Il permet 
également de récupérer le résultat de plusieurs requêtes SQL par l’intermédiaire d’API Rest.
