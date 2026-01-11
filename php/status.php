<?php
header("Content-Type: application/json");

$conn = new mysqli("localhost", "root", "", "plc_db");
$res = $conn->query("SELECT * FROM iotable WHERE id=0");
echo json_encode($res->fetch_assoc());

