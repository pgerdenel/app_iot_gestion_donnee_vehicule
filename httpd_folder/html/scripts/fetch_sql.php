<?php
/*
 * http://localhost:10080/scripts/fetch_sql.php?request_name=user_prosody
 * http://localhost:10080/scripts/fetch_sql.php?request_name=nb_vec
 * http://localhost:10080/scripts/fetch_sql.php?request_name=vit_moy
 * http://localhost:10080/scripts/fetch_sql.php?request_name=nb_acc
 * http://localhost:10080/scripts/fetch_sql.php?request_name=nb_jam
 * http://localhost:10080/scripts/fetch_sql.php?request_name=nb_zone
 */

/* GENERAL */
// header("Content-type: application/json");
// Désactiver le rapport d'erreurs
//error_reporting(0);


/* DB */
$request_name = "";
$host = 'mysqldb';
$port = "3306";
$db_name = 'proso';
$user = "rootrm";
$pass = "test";
$charset = 'utf8mb4';

/* VAR */
$result = fill_result("1", "default_message");

if(isset($_GET['request_name'])) {

    $request_name = $_GET['request_name'];
    // echo 'request '.$request_name.' called';

    // connexion PDO 
    $dbh = new PDO('mysql:host='.$host.';dbname='.$db_name, $user, $pass);

    switch ($request_name) {
        case 'user_prosody': // Tous les comptes utilisteurs Prosody enregistrés
            try {
                // on récupère tous les champs nom_user et password de la table prosody_user et prosody_pass
                $sth = $dbh->prepare('SELECT DISTINCT user from prosody');
                $sth->execute();
                $all_prosody_user = $sth->fetchAll(\PDO::FETCH_ASSOC);
                $result = fill_result(0, count($all_prosody_user) > 0 ? $all_prosody_user:["aucun utilisateur"]);
                
                // on ferme la connexion
                $dbh = null; 
            } 
            catch (PDOException $e) {
                // print "\nErreur !: " . $e->getMessage() . "<br/>";
                $result = fill_result(1, $e->getMessage());
                die();
            }
            break;
        case 'nb_vec': // Nombre de véhicule ayant été enregistré dans la base     
            try {
                // on récupère toutes les stationsID first dans la table accident
                $sth = $dbh->prepare('SELECT DISTINCT station_id_first from accident');
                $sth->execute();
                $all_station_id_accident_first = $sth->fetchAll(\PDO::FETCH_ASSOC);
            
                // on récupère toutes les stationsID last dans la table accident
                $sth = $dbh->prepare('SELECT DISTINCT station_id_last from accident');
                $sth->execute();
                $all_station_id_accident_last = $sth->fetchAll(\PDO::FETCH_ASSOC);
                
                /* ---- */

                // on récupère toutes les stationsID first dans la table embouteillage
                $sth = $dbh->prepare('SELECT DISTINCT station_id_first from embouteillage');
                $sth->execute();
                $all_station_id_jam_first = $sth->fetchAll(\PDO::FETCH_ASSOC);

                // on récupère toutes les stationsID second dans la table embouteillage
                $sth = $dbh->prepare('SELECT DISTINCT station_id_second from embouteillage');
                $sth->execute();
                $all_station_id_jam_second = $sth->fetchAll(\PDO::FETCH_ASSOC);

                // on récupère toutes les stationsID last dans la table embouteillage
                $sth = $dbh->prepare('SELECT DISTINCT station_id_last from embouteillage');
                $sth->execute();
                $all_station_id_jam_last = $sth->fetchAll(\PDO::FETCH_ASSOC);

                // on merge tous les tableaux et on enlève les doublons
                $final_array_station = array_unique(array_merge(
                    $all_station_id_accident_first,
                    $all_station_id_accident_last, 
                    $all_station_id_jam_first,
                    $all_station_id_jam_second,
                    $all_station_id_jam_last
                ), SORT_REGULAR);

                //  on met la taille du tableau dans $result
                $result = fill_result(0, strval(count($final_array_station)));

                $dbh = null;
            } 
            catch (PDOException $e) {
                print "\nErreur PDO !: " . $e->getMessage() . "<br/>";
                $result = fill_result(1, $e->getMessage());
                die();
            }
            break;
        case 'vit_moy': // Vitesse moyenne des véhicules ayant été enregistré dans la base
            try {
                // on récupère toutes les vitesse dans la table embouteillage
                $sth = $dbh->prepare('SELECT vitesse_moyenne from embouteillage');
                $sth->execute();
                $ar_vitesse = $sth->fetchAll(\PDO::FETCH_ASSOC );
                //print_r($ar_vitesse);
                $all_vitesse = array_sum(array_map(function($item) { // somme de tous les champ 'vitesse_moyenne' de chaque array d'array
                    return $item['vitesse_moyenne']; 
                }, $ar_vitesse));
                if(count($ar_vitesse) > 0) {
                    $result = fill_result(0, strval(round($all_vitesse/count($ar_vitesse), 1))); // on renvoie la moyenne de toutes les vitesses
                }
                else {
                    $result = fill_result(1, 0);
                }
                $dbh = null;
            }
            catch (PDOException $e) { // pdo erreur
                print "\nErreur PDO !: " . $e->getMessage() . "<br/>";
                $result = fill_result("1", $e->getMessage());
                die();
            }
            catch (Exception $e) { // general error
                print "\nErreur vit_moy: " . $e->getMessage() . "<br/>";
                $result = fill_result("1", $e->getMessage());
            }
            break;
        case 'nb_acc': // Nombre d'accident enregistré
            try {
                // on récupère le nombre d'accidentID dans la table accident
                $sth = $dbh->prepare('SELECT COUNT(accident_id) from accident');
                $sth->execute();
                $nb_accident = $sth->fetch(\PDO::FETCH_NUM);

                $result = fill_result(0, strval($nb_accident[0]));

                $dbh = null;
            }
            catch (PDOException $e) {
                print "\nErreur PDO !: " . $e->getMessage() . "<br/>";
                $result = fill_result("1", $e->getMessage());
                die();
            }
            break;
        case 'nb_jam': // Nombre d'embouteillage enregistré
            try {
                // on récupère le nombre d'embouteillage_id dans la table embouteillage
                $sth = $dbh->prepare('SELECT COUNT(embouteillage_id) from embouteillage');
                $sth->execute();
                $nb_jam = $sth->fetch(\PDO::FETCH_NUM);

                $result = fill_result(0, strval($nb_jam[0]));

                $dbh = null;
            }
            catch (PDOException $e) {
                print "\nErreur PDO !: " . $e->getMessage() . "<br/>";
                $result = fill_result(1, $e->getMessage());
                die();
            }
            break;
        case 'nb_zone': // Le nombre de zone(in ou out) surveillé
            try {
                // on récupère le nombre de zone in
                $sth = $dbh->prepare('SELECT COUNT(zonein_id) from zonein');
                $sth2 = $dbh->prepare('SELECT COUNT(zoneout_id) from zoneout');
                $sth->execute();
                $nb_zonein = $sth->fetch(\PDO::FETCH_NUM);
                $sth2->execute();
                $nb_zoneout = $sth2->fetch(\PDO::FETCH_NUM);
                $result = fill_result(0, strval($nb_zonein[0]+$nb_zoneout[0]));

                $dbh = null;
            }
            catch (PDOException $e) {
                print "\nErreur PDO !: " . $e->getMessage() . "<br/>";
                $result = fill_result(1, $e->getMessage());
                die();
            }
            break;
        default:
            echo 'request_name = '.$request_name." invalid";
            $result = fill_result(1, 'request_name = '.$request_name." invalid");
    }
}

function fill_result($code_p, $data_p) {
    $result = new stdClass(); // Estrict Mode
    $result->code = $code_p;
    $result->data = $data_p;
    return $result;
}

echo json_encode($result);

?>