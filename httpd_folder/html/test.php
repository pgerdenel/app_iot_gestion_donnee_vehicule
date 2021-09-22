<?php

phpinfo();

$host = 'mysqldb';
$port = "3306";
$db_name = 'proso';
$user = "rootrm";
$pass = "test";
$charset = 'utf8mb4';

/* TEST Driver PDO Disponible
if(in_array("mysql",PDO::getAvailableDrivers())){
    echo " You have PDO for MySQL driver installed \n";
}
else{
    echo "PDO driver for MySQL is not installed in your system\n";
}
*/

/* TEST Connexion DB avec PDO
try {
    $dbh = new PDO('mysql:host='.$host.';dbname='.$db_name, $user, $pass);
    foreach($dbh->query('SELECT * from stationtype') as $row) {
        print_r($row);
    }
    $dbh = null;
} 
catch (PDOException $e) {
    print "\nErreur !: " . $e->getMessage() . "<br/>";
    die();
}
*/

?>