// revoir les routes passés aux FREE BOSH (/accident ou /bouchon ou les 2)
var BOSH_SERVICE = 'http://localhost:15280/http-bind';

var connectionFreeBosh1     = null;
var connectionFreeBosh2     = null;
var connectionAccident      = null;
var connectionBouchon       = null;
var show_log                = true;
var id_log_free_bosh_1      = '#log_free_bosh_1';
var id_log_free_bosh_2      = '#log_free_bosh_2';
var id_log_accident         = '#log_accident';
var id_log_bouchon          = '#log_bouchon';
var show_sytem_msg          = false;
var jid_accident            = "user_apache@localhost/accident";
var jid_bouchon             = "user_apache@localhost/bouchon";
var pass                    = "test";

var php_script              = "scripts/";

var ar_msg_acc_current      = []; 
var ar_msg_jam_current      = []; 
var current_index_acc       = -1; 
var current_index_jam       = -1; 

var ar_msg_log              = [];  // { "acc1" : "msg_content", "jam1" : "msg_content"}
var id_log_accident         = "#log_accident";
var id_log_jam              = "#log_jam";


console.log = function() {}

/* Fonction permettant de stocker les messages à logger dans un tableau
 * Fonction permettant de les stocker dans un tableau associatif (indentifiant unique => HTML_TO_APPEND)
 * Renvoie l'id unique (clé)
 */
function store_msg(type, msg) {
    console.log("STORE MESSAGE CALLED");

    // on génère un nouvel id pour le msg
    let id = current_index_acc+1;
    msg = "<div style='padding-left:1em;margin-top:0.2em;'>"+msg+"</div>";

    // on insère le message dans le tableau
    if(type==='acc') {
        //ar_msg_acc_current[id] = msg; 
        ar_msg_acc_current.push({id: id, msg: msg});
        //console.log("ar_msg_acc_current[id]= "+JSON.stringify(ar_msg_acc_current[id]));
        console.debug("########## l'accident a été sauvegardé dans le tableau courant ####");
        console.log("accident stocké !");
        console.log("tableau ACCIDENT courant : ");
        display_tab(ar_msg_acc_current);
    } 
    else if(type==='jam') {
        //ar_msg_jam_current[id] = msg;
        ar_msg_jam_current.push({id: id, msg: msg});
        //console.log("ar_msg_jam_current[id]= "+ar_msg_jam_current[id].msg);
        console.debug("########## le jam a été sauvegardé dans le tableau courant ####");
        console.log("bouchon stocké !");
        console.log("tableau BOUCHON courant : ");
        display_tab(ar_msg_jam_current);
    }
    else {
        console.log("type non géré");
    }
    
    // on incrémente l'index
    current_index_acc+=1;

    // on copie ce message dans le tableau d'historique des évènements' dans 15sec + 5mn
    setTimeout(function(){
        ar_msg_log.push({id: id, msg: msg+"<br/>"});
        console.debug("# MSG a été svg dans l'historique ####");
        display_tab(ar_msg_log);
    }, 10000); /* 315000 rappel après 5mn et 15 secondes = 315 millisecondes */

    // on supprimera cette valeur du tableau d'évenements courant dans 30sec + 5mn
    setTimeout(function(){
        delete_msg(type, id)
    }, 15000 ); /* 330000 rappel après 5mn et 30 secondes = 330 millisecondes */
}
/* Fonction permettant de supprimer un élément d'un tableau associatif 
 * type 'acc', 'jam'
 */
function delete_msg(type_msg, msg_id) {
    console.log("delete_msg called ");
    if (type_msg=== 'acc') {
        if (ar_msg_acc_current.hasOwnProperty(msg_id)) {
            delete ar_msg_acc_current[msg_id];
            load_msg(type_msg);
            console.debug("# ACCIDENT a été supprimé du tableau courant ####");
        }
    }
    else if (type_msg=== 'jam') {
        if (ar_msg_jam_current.hasOwnProperty(msg_id)) {
            delete ar_msg_jam_current[msg_id];
            load_msg(type_msg);
            console.debug("# JAM a été supprimé du tableau courant ####");
        }
    }
    else if (type_msg==='syst') {
        console.debug("message syst on fait rien");
    }
    else {
        console.error('delete_msg() type de message incorrecte= '+type_msg);
    }
}

function load_msg(type_msg) {
    console.log("load_msg called ");
    if (type_msg=== 'acc') {
        $(id_log_accident).empty();
        for(var key in ar_msg_acc_current) {
            $(id_log_accident).append(ar_msg_acc_current[key].msg);
        }
        console.debug("# ACCIDENT chargés depuis le tableau courant ####");
    }
    else if (type_msg=== 'jam') {
        $(id_log_bouchon).empty();
        for(var key in ar_msg_jam_current) {
            $(id_log_bouchon).append(ar_msg_jam_current[key].msg);
        }
        console.debug("# JAM chargés depuis le tableau courant ####");
    }
    else if (type_msg==='syst') {
        console.debug("message syst on fait rien");
    }
    else {
        console.error('load_msg() type de message incorrecte= '+type_msg);
    }
}

function display_tab(tab) {
    for(var key in tab) {
        console.log(tab[key]);
    } 
}
/* Fonction de log_syst */
function log_syst(id_log, msg) 
{ 
    if (msg != null)
        $(id_log).append('<div style=\'padding-left:1em;margin-top:0.2em;\'>'+msg+'</div>');
}
/* Fonction permettant de logger les messages */
// Fonction permettant de logger les messages de FreeBosh1
function log_msg(id_log, type_msg, msg) 
{
    console.log("LOG_MSG CALLED type_msg = "+type_msg);

    // Récupère le type de message
    if(type_msg==='acc') {
        $(id_log).empty();
        //console.log("on parcout le ar_msg_acc_current size= "+ar_msg_acc_current.length);
        //display_tab(ar_msg_acc_current);
        for(var key in ar_msg_acc_current) {
            $(id_log).append(ar_msg_acc_current[key].msg);
            console.debug("########## l'accident a été affiché depuis le tab courant ####");
            //console.log("on affiche le message accident = "+ar_msg_acc_current[key].msg);
        }
          
    }
    else if (type_msg==='jam') {
        $(id_log).empty();
        //console.log("on parcout le ar_msg_jam_current size= "+ar_msg_jam_current.length);
        for(var key in ar_msg_jam_current) {
            $(id_log).append(ar_msg_jam_current[key].msg);
            console.debug("########## le jam a été affiché depuis le tab courant ####");
        }  
    }
    else {
        console.error('log() type de message incorrecte= '+type_msg);
    }
};

// Fonction permettant d'afficher les données recues
function rawInputFreeBosh(id_log, data)
{   
    // log('RECV: on reçoit les données suivantes : ' + data);
    
    // On format 
    data = data.replaceAll("&quot;", "\""); // HTML entity &quote;
    console.log("data= "+data);

    //console.log("id_log= "+id_log);

    let from_jid="";
    let to_jid="";
    let msg_content="";
    let resource = "";
    let isFromTchat=false;
    let isFromAccident=false;
    let isFromBouchon=false;
    let isFromAdmin=false;
    let isSystem=false;
    let type_vehicule = "";
    let type_msg = "";

    var date = new Date();
    var hms = "<b>"+date.toLocaleTimeString()+"</b>\t";

    // on vérifie si le message nous intérresse et contient "<message from=" et donc provient d'un utilisateur (pas du système)
    if(data.includes("<message from=")) {
        //console.log("'<message from= présent', donc ce message nous intérresse");
        try {
            // on récupère le JID de l'émetteur du message
            // on définit les occurrences délimitant la droite et la gauche de la valeur à récupérer
            let delimitor_JID_left = "<message from=\"";
            let delimitor_JID_right = "\" id=\"";
            // 1ere découpe
            from_jid = data.substring(data.indexOf(delimitor_JID_left), data.indexOf(delimitor_JID_right)); 
            // on remplace les occurrences des 2 délimiteurs par rien
            from_jid= from_jid.replace(delimitor_JID_left, "");
            from_jid= from_jid.replace(delimitor_JID_right, "");

            // on récupère le JID a qui le message était destiné (user_apache@localhost oui on le sait) mais on veut la ressource !!
            // on définit les occurrences délimitant la droite et la gauche de la valeur à récupérer
            let delimitor_to_JID_left = "to=\"";
            let delimitor_to_JID_right = "\" xmlns";
            // 1ere découpe
            to_jid_cut = data.substring(data.indexOf(delimitor_to_JID_left), data.length); 
            // 2eme découpe
            to_jid = to_jid_cut.substring(to_jid_cut.indexOf(delimitor_to_JID_left), to_jid_cut.indexOf(delimitor_to_JID_right)); 
            // on remplace les occurrences des 2 délimiteurs par rien
            to_jid= to_jid.replace(delimitor_to_JID_left, "");
            to_jid= to_jid.replace(delimitor_to_JID_right, "");

            // on récupère la resource pointée (ex: /accident) par le JID destinataire (to) et on enlève le '/' de départ
            resource = to_jid.substr(to_jid.indexOf('/'), to_jid.length).substring(1).toUpperCase(); 
            
            // on récupère le contenu du message
            // on définit les occurrences délimitant la droite et la gauche de la valeur à récupérer
            let delimitor_MSG_left = "><body>";
            let delimitor_MSG_right = "</body><";
            // on récupère la chaine à partir du délimiteur gauche compris jusqu'au délimiteur droit compris
            msg_content = data.substring(data.indexOf(delimitor_MSG_left), data.indexOf(delimitor_MSG_right)); 
            // on remplace les occurrences des 2 délimiteurs par rien
            msg_content= msg_content.replace(delimitor_MSG_left, "");
            msg_content= msg_content.replace(delimitor_MSG_right, "");

            // on vérifie s'il s'agit d'un message /accident ou /bouchon
            isFromAccident = to_jid.includes("accident");
            isFromBouchon = to_jid.includes("bouchon");

            // on check s'il s'agit d'un message envoyé d'un client comme pidgin ou provenant de l'application
            isFromTchat = data.includes("type=\"chat\"");

            // on check s'il s'agit d'un message envoyé par un admin
            isFromAdmin = data.includes("admin@");

            // on check s'il s'agit d'un message système
            // isSystem = (isFromAccident?false:(isFromBouchon?false:(isFromAdmin?false:true)))
            isSystem = !isFromTchat && !isFromAccident && !isFromBouchon && !isFromAdmin
         }
         catch(e) {
             console.error("traitement rawInput ERROR= "+JSON.stringify(e))
         }
         finally {
             console.log("from_jid= |"+from_jid+"|");
             console.log("to_jid= |"+to_jid+"|");
             console.log("msg_content = |"+msg_content+"|");
             console.log("resource= " + resource);
             console.log("isFromAccident= "+isFromAccident);
             console.log("isFromBouchon= "+isFromBouchon);
             console.log("isFromTchat= "+isFromTchat);
             console.log("isFromAdmin= "+isFromAdmin);
             console.log("isSystem= "+isSystem);
            //  (isFromAccident?"accident":"bouchon")
            //  (isFromBouchon?"bouchon":"admin")
            //  (isFromAdmin?"admin":"systeme")
         }
    }
    else {
        //console.log("on skip le message (<message from= absent)");
        isSystem = true;
    }
    
    let msg= null;
     // si ce n'est pas un message system
    if(!isSystem) {
        console.log("ce n'est pas un message system");
        if(to_jid.includes('accident')) {
            type_msg='acc';
            msg_content = JSON.parse(msg_content);
            type_vehicule = (msg_content[0]['stationType'] === 5)?"ordinaire":(msg_content[0]['stationType'] === 10)?"d'urgence":(msg_content[0]['stationType'] === 15)?"opérateur":"de type non répertorié";
            type_vehicule2 = (msg_content[1]['stationType'] === 5)?"ordinaire":(msg_content[1]['stationType'] === 10)?"d'urgence":(msg_content[1]['stationType'] === 15)?"opérateur":"de type non répertorié";
            console.log("msg_content "+msg_content[0]);
            msg = hms+"</span>"+
            " <span style=\'color:red;\'><b>"+resource+"</b></span>"+ 
            " signalé entre un véhicule <span style=\'color:green;\'>"+type_vehicule+"</span>"+
            " immatriculé <span style=\'color:blue;\'>"+msg_content[0]['stationID']+"</span>"+
            " et un véhicule <span style=\'color:green;\'>"+type_vehicule2+"</span>"+
            " immat <span style=\'color:blue;\'>"+msg_content[1]['stationID']+"</span>"+
            " à la position GPS <span style=\'color:orange;font-size:0.7rem;\'>"+msg_content[0]['position']+"</span>";
            store_msg(type_msg, msg);
            setTimeout(log_msg(id_log, type_msg, msg), 250); // 250ms
        }
        else if(to_jid.includes('bouchon')) {
            type_msg = 'jam';
            msg_content = JSON.parse(msg_content);
            console.log("msg_content "+msg_content[0]);
            msg = hms+" <span style=\'color:red;\'><b>"+resource+"</b></span>"+ 
            " signalé à la position GPS <span style=\'color:orange;font-size:1rem;\'>"+msg_content[0]['position']+"</span>"+
            " (heading ~ <span style=\'color:green;\'> "           +Math.trunc( (parseFloat(msg_content[0]['heading'])+parseFloat(msg_content[1]['heading'])+parseFloat(msg_content[2]['heading'])) / 3 ) +"</span>) "+
            " avec pour vitesse moyenne <span style=\'color:purple;\'>" +Math.trunc( (parseFloat(msg_content[0]['vitesse'])+parseFloat(msg_content[1]['vitesse'])+parseFloat(msg_content[2]['vitesse'])) / 3 ) +"</span>";
            store_msg(type_msg, msg);
            setTimeout(log_msg(id_log, type_msg, msg), 250); // 250ms
        }
        else {
            console.log("cette ressource n'est pas encore gérée");
        }
    } 
    else if (isSystem) { // si c'est un message system et qu'on les affiche
        type_msg = 'syst';
        console.log("c'est un message system");
        if (show_sytem_msg) {
            msg = hms+" MSG RECUE <b>"+resource+"</b> RECUE de type "+(isFromAccident?"accident":(isFromBouchon?"bouchon":(isFromAdmin?"admin":"systeme")))+" avec pour contenu |"+(isSystem)?data+"\n\n":msg_content+"|";
            log_syst(id_log, msg);
        }
        else { 
            console.log("mais leur affichage est sur off");
        }
    }
    else {
        type_msg = 'autres';
        console.log("c'est un message autres");
        // console.log("cas chelou");
        // console.log("isSystem= "+isSystem);
        // console.log("show_sytem_msg= "+show_sytem_msg);
    }
    
}
// Fonction permettant d'afficher les données envoyées
function rawOutputFreeBosh(id_log, data)
{
    // log('SENT: ' + data);
    //console.log("id_log= "+id_log);
    //console.log("data= "+data);
}
// Fonction permettant de gérer le label l'état de la connexion
function onConnectFreeBosh(id_log, status)
{
    //console.log("status= "+status);
    //console.log("id= "+id_log);
    if (status == Strophe.Status.CONNECTING) {
	log_syst(id_log, 'Strophe is connecting.');

    } else if (status == Strophe.Status.CONNFAIL) {
        log_syst(id_log, 'Strophe failed to connect.');
	//showConnect(); // provoque des bugs d'affichage a debugguer
    } else if (status == Strophe.Status.DISCONNECTING) {
        log_syst(id_log, 'Strophe is disconnecting.');
    } else if (status == Strophe.Status.DISCONNECTED) {
        log_syst(id_log, 'Strophe is disconnected.');
	//showConnect(); // provoque des bugs d'affichage a debugguer
    } else if (status == Strophe.Status.CONNECTED) {
        log_syst(id_log, 'Strophe is connected.');
    
	// Start up disco browser
	//browser.showBrowser();
    }
}
// Permet de gérer l'état des boutons en connexion
function showConnect(id_jid, id_pass, id_btn_connect)
{
    var jid = $(id_jid);
    var pass = $(id_pass);
    var button = $(id_btn_connect).get(0);	

    jid.removeAttr('disabled');
    pass.removeAttr('disabled');
    button.value = 'connect';

    return false;
}
// Permet de gérer l'état des boutons en déconnexion
function showDisconnect(id_jid, id_pass, id_btn_connect)
{
    var jid = $(id_jid);
    var pass = $(id_pass);
    var button = $(id_btn_connect).get(0);	

    button.value = 'disconnect';
    pass.attr('disabled','disabled');
    jid.attr('disabled','disabled');

    return false;
}

// Fonction permettant de connecter directement le client a la resource Accident
function connectAccident() {

    // ACCIDENT
    connectionAccident              = new Strophe.Connection(BOSH_SERVICE);
    connectionAccident.rawInput     = rawInputFreeBosh.bind(null, id_log_accident);
    connectionAccident.rawOutput    = rawOutputFreeBosh.bind(null, id_log_accident);
    id_sytem_accident               = false;
    
    connectionAccident.connect(
        jid_accident, 
        pass, 
        onConnectFreeBosh.bind(null, id_log_accident),
        60,
        1,
        "accident_route" // paramètre optionel de la route
        );
}
function connectBouchon() {

    // BOUCHON
    connectionBouchon              = new Strophe.Connection(BOSH_SERVICE);
    connectionBouchon.rawInput     = rawInputFreeBosh.bind(null, id_log_bouchon);
    connectionBouchon.rawOutput    = rawOutputFreeBosh.bind(null, id_log_bouchon);
    id_sytem_bouchon               = false;

    connectionBouchon.connect(
        jid_bouchon, 
        pass, 
        onConnectFreeBosh.bind(null, id_log_bouchon),
        60,
        1,
        "bouchon_route" // paramètre optionel de la route
        );
}

$(document).ready(function () {
    
    /* INITIALISATION */

    // GENERAL
    $('#show_system_msg').prop('checked', false);
    show_sytem_msg = false;

    // ACCIDENT
    connectAccident();

    // BOUCHON
    connectBouchon();

    // FREE BOSH 1
    connectionFreeBosh1             = new Strophe.Connection(BOSH_SERVICE);
    connectionFreeBosh1.rawInput    = rawInputFreeBosh.bind(null, id_log_free_bosh_1);
    connectionFreeBosh1.rawOutput   = rawOutputFreeBosh.bind(null, id_log_free_bosh_1);
    id_sytem_free_bosh_1            = false;

    // FREE BOSH 2
    connectionFreeBosh2             = new Strophe.Connection(BOSH_SERVICE);
    connectionFreeBosh2.rawInput    = rawInputFreeBosh.bind(null, id_log_free_bosh_2);
    connectionFreeBosh2.rawOutput   = rawOutputFreeBosh.bind(null, id_log_free_bosh_2);
    id_sytem_free_bosh_2            = false;

    // HANDLER CLICK SUR BOUTON CONNEXION/DECONNEXION
    $('#connect_free_bosh1').bind('click', function () {

        var button = $('#connect_free_bosh1').get(0);
        var jid = $('#jid_free_bosh1');
        var pass = $('#pass_free_bosh1');	
        
        if(connectionFreeBosh1 == null) {
            connectionFreeBosh1 = new Strophe.Connection(BOSH_SERVICE);
            connectionFreeBosh1.rawInput = rawInputFreeBosh.bind(null, id_log_free_bosh_1);
            connectionFreeBosh1.rawOutput = rawOutputFreeBosh.bind(null, id_log_free_bosh_1);
        }
        else {
            console.log("connection n'st pas null")
        }
        

        if (button.value == 'connect') {
            //console.log("connect value detected");
            showDisconnect('#jid_free_bosh1', '#pass_free_bosh1', '#connect_free_bosh1', '#label', '#anon');
            // on spécifie la room à rejoindre
            /*
             * (String) jid	The user’s JID.  This may be a bare JID, or a full JID.  If a node is not supplied, SASL OAUTHBEARER or SASL ANONYMOUS authentication will be attempted (OAUTHBEARER will process the provided password value as an access token).
             * (String) pass	The user’s password.
             * (Function) callback	The connect callback function.
             * (Integer) wait	The optional HTTPBIND wait value.  This is the time the server will wait before returning an empty result for a request.  The default setting of 60 seconds is recommended.
             * (Integer) hold	The optional HTTPBIND hold value.  This is the number of connections the server will hold at one time.  This should almost always be set to 1 (the default).
             * (String) route	The optional route value.
             * (String) authcid	The optional alternative authentication identity (username) if intending to impersonate another user.  
             *                  When using the SASL-EXTERNAL authentication mechanism, for example with client certificates, then the authcid value is used to determine whether an authorization JID (authzid) should be sent to the server.  
             *                  The authzid should not be sent to the server if the authzid and authcid are the same.  
             *                  So to prevent it from being sent (for example when the JID is already contained in the client certificate), set authcid to that same JID.  See XEP-178 for more details.
             */   
            connectionFreeBosh1.connect(
                jid.get(0).value+"/accident", // le "/qqch", içi "/accident" correspond à la resource cf python
                pass.get(0).value, 
                onConnectFreeBosh.bind(null, id_log_free_bosh_1),
                60,
                1,
                "accident_route" // paramètre optionel de la route
                );
        } else if(button.value == 'disconnect') {
            //console.log("disconnect value detected");
            connectionFreeBosh1.disconnect();
            var connectionFreeBosh1   = null; // obligatoire sinon génère une erreur T is null
            showConnect('#jid_free_bosh1', '#pass_free_bosh1', '#connect_free_bosh1', '#label', '#anon');
        } else {
            console.error("la valeur du bouton n'est pas défini");
        }
	    return false;
    });
    $('#connect_free_bosh2').bind('click', function () {

        var button = $('#connect_free_bosh2').get(0);
        var jid = $('#jid_free_bosh2');
        var pass = $('#pass_free_bosh2');	
        
        if(connectionFreeBosh2 == null) {
            connectionFreeBosh2 = new Strophe.Connection(BOSH_SERVICE);
            connectionFreeBosh2.rawInput = rawInputFreeBosh.bind(null, id_log_free_bosh_2);
            connectionFreeBosh2.rawOutput = rawOutputFreeBosh.bind(null, id_log_free_bosh_2);
        }
        else {
            console.log("connection n'st pas null")
        }
        

        if (button.value == 'connect') {
            //console.log("connect value detected");
            showDisconnect('#jid_free_bosh2', '#pass_free_bosh2', '#connect_free_bosh2');
            // on spécifie la room à rejoindre
            /*
             * (String) jid	The user’s JID.  This may be a bare JID, or a full JID.  If a node is not supplied, SASL OAUTHBEARER or SASL ANONYMOUS authentication will be attempted (OAUTHBEARER will process the provided password value as an access token).
             * (String) pass	The user’s password.
             * (Function) callback	The connect callback function.
             * (Integer) wait	The optional HTTPBIND wait value.  This is the time the server will wait before returning an empty result for a request.  The default setting of 60 seconds is recommended.
             * (Integer) hold	The optional HTTPBIND hold value.  This is the number of connections the server will hold at one time.  This should almost always be set to 1 (the default).
             * (String) route	The optional route value.
             * (String) authcid	The optional alternative authentication identity (username) if intending to impersonate another user.  
                               When using the SASL-EXTERNAL authentication mechanism, for example with client certificates, then the authcid value is used to determine whether an authorization JID (authzid) should be sent to the server.  
                               The authzid should not be sent to the server if the authzid and authcid are the same.  
                               So to prevent it from being sent (for example when the JID is already contained in the client certificate), set authcid to that same JID.  See XEP-178 for more details.
             */
            connectionFreeBosh2.connect(
                jid.get(0).value+"/accident", // le "/qqch", içi "/accident" correspond à la resource cf python
                pass.get(0).value, 
                onConnectFreeBosh.bind(null, id_log_free_bosh_2),
                60,
                1,
                "accident_route" // paramètre optionel de la route
                );
        } else if(button.value == 'disconnect') {
            //console.log("disconnect value detected");
            connectionFreeBosh2.disconnect();
            var connectionFreeBosh2   = null; // obligatoire sinon génère une erreur T is null
            showConnect('#jid_free_bosh2', '#pass_free_bosh2', '#connect_free_bosh2');
        } else {
            console.error("la valeur du bouton n'est pas défini");
        }
	    return false;
    });

    // HANDLER CLICK | CLEAN | ACCIDENT => on clean les logs de la fenêtre ACCIDENT
    $("#clean_accident").bind('click', function () {
	    $(id_log_accident).html("");
    });
    // HANDLER CLICK | CLEAN | BOUCHON => on clean les logs de la fenêtre BOUCHON
    $("#clean_bouchon").bind('click', function () {
        $(id_log_bouchon).html("");
    });
    // HANDLER CLICK | CLEAN | FREEBOSH1 => on clean les logs de la fenêtre freebosh1
    $("#clean_free_bosh1").bind('click', function () {
	    $(id_log_free_bosh_1).html("");
    });
    // HANDLER CLICK | CLEAN | FREEBOSH2 => on clean les logs de la fenêtre freebosh1
    $("#clean_free_bosh2").bind('click', function () {
	    $(id_log_free_bosh_2).html("");
    });

    // HANDLER CLICK HREF LOG TITLE (afficher/masquer les logs)
    $("#log_container_accident").bind('click', function () {
        $(id_log_accident).toggle();	
    });
    $("#log_container_bouchon").bind('click', function () {
        $(id_log_bouchon).toggle();	
    });
    $("#log_container_free_bosh_1").bind('click', function () {
        $(id_log_free_bosh_1).toggle();	
    });
    $("#log_container_free_bosh_2").bind('click', function () {
        $(id_log_free_bosh_2).toggle();	
    });

    // HANDLER CLICK | SHOW SYSTEM MESSAGE
    $('#show_system_msg').change(function() {
        //console.log("le toogle est à "+$(this).prop('checked'));
        //console.log("le toogle est à "+$('#show_system_msg_bosh_1').prop('checked'));
        show_sytem_msg = $('#show_system_msg').prop('checked');
    });

    // HANDLER CLICK | BOUTON SATS MODAL MySQL STATS
    $("#show_stats").click(function() {
        doSQLRequest();
    });

    // HANDLER CLICK | REFRESH MODAL MySQL STATS
    $("#refreshStats").click(function() {
        // on lance toutes les fonctions AJAX MySQL
        doSQLRequest();
    });

    // HANDLER CLICK | BOUTON HIST MODAL
    $("#show_hist").click(function() {
        //console.log("on show hist() "+JSON.stringify(ar_msg_log));
        $("#wrapper_hist").empty();
        for(var key in ar_msg_log) {
            $("#wrapper_hist").append(ar_msg_log[key].msg);
        }
    });

    // HANDLER CLICK | REFRESH MODAL HIST MODAL
    $("#refreshHist").click(function() {
        //console.log("on show hist() "+JSON.stringify(ar_msg_log));
        $("#wrapper_hist").empty();
        for(var key in ar_msg_log) {
            $("#wrapper_hist").append(ar_msg_log[key].msg);
        }
    });

    
});


function doSQLRequest() {
    fetchAllProsodyUser();
    fetchAllNbVec();
    fetchVitMoy();
    fetchAllNbAcc();
    fetchAllNbJam();
    fetchNbZone();
}
// Requête AJAX PHP : Tous les comptes Prosody enregistrés	
function fetchAllProsodyUser() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        console.log("fetchAllProsodyUser response= "+this.responseText);
        var respJSON = JSON.parse(xmlhttp.responseText);
        console.log("fetchAllProsodyUser response respJSON= "+JSON.stringify(respJSON));
        document.getElementById("wrapper_response_req1").innerHTML = (respJSON['code'] == 0)?
        getNewArray(respJSON['data']).join(",\n")
        :"erreur de requête";
      }
    };
    xmlhttp.open("GET",php_script+"fetch_sql.php?request_name="+"user_prosody",true);
    xmlhttp.send();
}     
function getNewArray(ar){
    array_user_name = []
    ar.forEach(element => {
        if(!element['user'].includes('20'))
            array_user_name.push(element['user']);
    });
    return array_user_name
}   
// Requête AJAX PHP : Nombre de véhicule ayant été enregistré dans la base
function fetchAllNbVec() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var respJSON = JSON.parse(xmlhttp.responseText);
        console.log("fetchAllNbVec response= "+this.responseText)
        document.getElementById("wrapper_response_req2").innerHTML = (respJSON['code'] == 0)?
        "Il y a <u>"+respJSON['data']+"</u> véhicules impliqués dans les évènements enregistrés en DB":
        "erreur de requête";
      }
    };
    xmlhttp.open("GET",php_script+"fetch_sql.php?request_name="+"nb_vec",true);
    xmlhttp.send();
} 
// Requête AJAX PHP : Vitesse moyenne des véhicules ayant été enregistré dans la base
function fetchVitMoy() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        console.log("fetchVitMoy response= "+this.responseText);
        var respJSON = JSON.parse(xmlhttp.responseText);
        console.log("fetchVitMoy response= "+this.respJSON);
        document.getElementById("wrapper_response_req3").innerHTML = (respJSON['code'] == 0)?
        "La vitesse moyenne des véhicules en embouteillage est de  <u>"+respJSON['data']+"</u> km/h":
        "erreur de requête";
      }
    };
    xmlhttp.open("GET",php_script+"fetch_sql.php?request_name="+"vit_moy",true);
    xmlhttp.send();
}
// Requête AJAX PHP : Nombre d'accident enregistré
function fetchAllNbAcc() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var respJSON = JSON.parse(xmlhttp.responseText);      
        console.log("fetchAllNbAcc response= "+this.responseText)
        document.getElementById("wrapper_response_req4").innerHTML = (respJSON['code'] == 0)?
        "Actuellement  <u>"+respJSON['data']+"</u> accidents ont été signalés":
        "erreur de requête";
      }
    };
    xmlhttp.open("GET",php_script+"fetch_sql.php?request_name="+"nb_acc",true);
    xmlhttp.send();
}
// Requête AJAX PHP : Nombre d'embouteillage enregistré
function fetchAllNbJam() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var respJSON = JSON.parse(xmlhttp.responseText);   
        console.log("fetchAllNbJam response= "+this.responseText)
        document.getElementById("wrapper_response_req5").innerHTML = (respJSON['code'] == 0)?
        "Actuellement  <u>"+respJSON['data']+"</u> embouteillages ont été signalés":
        "erreur de requête";
      }
    };
    xmlhttp.open("GET",php_script+"fetch_sql.php?request_name="+"nb_jam",true);
    xmlhttp.send();
}
// Requête AJAX PHP : Le nombre de zone in et out surveillées
function fetchNbZone() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var respJSON = JSON.parse(xmlhttp.responseText);   
        console.log("fetchNbZone response= "+this.responseText)
        document.getElementById("wrapper_response_req6").innerHTML = (respJSON['code'] == 0)?
        "Notre périmètre d'action se compose de  <u>"+respJSON['data']+"</u> zones en surveillance constante":
        "erreur de requête";
      }
    };
    xmlhttp.open("GET",php_script+"fetch_sql.php?request_name="+"nb_zone",true);
    xmlhttp.send();
}



// découpe une chaine situé entre 2 séparateurs
function splitString(stringToSplit, separator) {
    var arrayOfStrings = stringToSplit.split(separator);
  
    console.log('La chaine d\'origine est : "' + stringToSplit + '"');
    console.log('Le délimiteur est : "' + separator + '"');
    console.log("Le tableau comporte " + arrayOfStrings.length + " elements : ");
    
    for (var i=0; i < arrayOfStrings.length; i++) {
        console.log("N°" + i + " = " + arrayOfStrings[i] + " / ");
    }
    return arrayOfStrings;
}