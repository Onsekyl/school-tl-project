<?php

$myfile = fopen("secrets-showdata.txt", "r") or die("Unable to open file!");
$user = fgets($myfile);
$pswd = fgets($myfile);
fclose($myfile);
$user = rtrim($user);
$pswd = rtrim($pswd);

$servername = "172.20.241.128";
$username = $user;
$password = $pswd;
$dbname = "measurements";
$groupid = 2; // We use this to recognise the exact measurement

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
        }

$sql = "SELECT groupid, sensorvalue_x, sensorvalue_y, sensorvalue_z, sensor_direction FROM rawdata WHERE groupid = $groupid ORDER BY id DESC LIMIT 100";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
   while($row = $result->fetch_assoc()) {
      echo  " - Sensor X: " . $row["sensorvalue_x"] . " - Sensor Y: " . $row["sensorvalue_y"]. " - Sensor Z: " . $row["sensorvalue_z"]. " - Sensor Direction " . $row["sensor_direction"] ."<br>" ;   }
}

$conn->close();
?>
