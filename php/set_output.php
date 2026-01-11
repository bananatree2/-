<?php
$data = json_decode(file_get_contents("php://input"), true);
$ch = intval($data["channel"]);
$val = intval($data["value"]);

$conn = new mysqli("localhost", "root", "", "plc_db");
$conn->query("UPDATE iotable SET output$ch=$val WHERE id=0");
