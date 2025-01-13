<?php
// Koble til databasen
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "attendance_bachelor_data";

// Opprett tilkobling
$conn = new mysqli($servername, $username, $password, $dbname);

// Sjekk tilkobling
if ($conn->connect_error) {
    die(json_encode(["status" => "error", "message" => "Connection failed: " . $conn->connect_error]));
}

// Logg start av script
error_log("Starter behandling av RFID-forespørsel.");

// Motta UID fra Arduino (via HTTP POST)
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    if (isset($_POST['rfid_tag'])) {
        $rfid_tag = trim($_POST['rfid_tag']); // Trim uønsket whitespace
        error_log("Mottatt RFID fra klient: $rfid_tag"); // Logg mottatt RFID

        // Sjekk om RFID finnes i `members`-tabellen fra databasen
        $stmt = $conn->prepare("SELECT student_number, name FROM members WHERE rfid_tag = ?");
        $stmt->bind_param("s", $rfid_tag);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $student_number = $row['student_number'];
            $member_name = $row['name']; // Hent navn som matcher med student nummer fra databasen

            error_log("RFID gjenkjent for: $member_name med studentnummer: $student_number");

            // Sjekk om det allerede er en `check_in` for samme dag uten `check_out`slik at vi får logget riktig tidspunkt  
            $date = date('Y-m-d');
            $check_stmt = $conn->prepare("SELECT * FROM attendance_log WHERE student_number = ? AND DATE(check_in) = ? AND check_out IS NULL");
            $check_stmt->bind_param("is", $student_number, $date);
            $check_stmt->execute();
            $check_result = $check_stmt->get_result();

            if ($check_result->num_rows > 0) {
                // Oppdater `check_out`
                $update_stmt = $conn->prepare("UPDATE attendance_log SET check_out = NOW(), 
                                               duration = duration + TIMESTAMPDIFF(SECOND, check_in, NOW()) / 3600
                                               WHERE student_number = ? AND DATE(check_in) = ? AND check_out IS NULL");
                $update_stmt->bind_param("is", $student_number, $date);
                $update_stmt->execute();

                error_log("Utsjekk registrert for $member_name");
                echo json_encode(["status" => "success", "message" => "Utsjekk registrert for $member_name!"]);
            } else {
                // Logg ny innsjekk
                $insert_stmt = $conn->prepare("INSERT INTO attendance_log (student_number, check_in, duration) VALUES (?, NOW(), 0)");
                $insert_stmt->bind_param("i", $student_number);
                $insert_stmt->execute();

                error_log("Innsjekk registrert for $member_name");
                echo json_encode(["status" => "success", "message" => "Innsjekk registrert for $member_name!"]);
            }
        } else {
            error_log("RFID ikke gjenkjent: $rfid_tag");
            echo json_encode(["status" => "error", "message" => "RFID ikke gjenkjent."]);
        }
    } else {
        error_log("Ingen RFID mottatt i forespørselen.");
        echo json_encode(["status" => "error", "message" => "Ingen RFID-tag mottatt."]);
    }
} else {
    error_log("Ugyldig forespørsel: Metoden er ikke POST.");
    echo json_encode(["status" => "error", "message" => "Ugyldig forespørsel."]);
}

$conn->close();
