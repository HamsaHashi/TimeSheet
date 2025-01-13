#include <SPI.h>
#include <MFRC522.h>
#include <WiFiS3.h>
#include <WiFiServer.h>

// RFID pins
#define SS_PIN 10
#define RST_PIN 5
MFRC522 rfid(SS_PIN, RST_PIN); // Initialiser RFID-leseren

// WiFi detaljer (HUSKHUSK!! bytte til statisk ip for å bruke fra flere enheter senere)
const char* ssid = "iPhone_230"; 
const char* password = "xxxxxxxxx"; 

// Server-URL og port
const char* serverHost = "1xxx72.2000.1000.7000000";
const int serverPort = 80;

// HTTP-server for GUI
WiFiServer wifiServer(8080);

// Variabel for lagrret RFID
String lastRFID = "";

void setup() {
  
  Serial.begin(9600);

  // Start SPI og RFID
  SPI.begin();
  rfid.PCD_Init();

  // Koblerr til WiF
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Start HTTP-servernen
  wifiServer.begin();
  Serial.println("HTTP-server started on port 8080");
}

void loop() {
  // Sjekk om en ny RFID er tilgjengelig
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    // Hent UID fra RFID-kortet
    String rfidTag = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      rfidTag += String(rfid.uid.uidByte[i], HEX);
    }
    rfidTag.toUpperCase(); // Konverter UID til store bokstaver
    Serial.println("RFID Tag: " + rfidTag);

    // Lagre siste RFID for GUI
    lastRFID = rfidTag;

    // Send UID til serveren via HTTP POST
    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;

      // Koble til serveren
      if (client.connect(serverHost, serverPort)) {
        Serial.println("Connected to server");

        // Lag HTTP POST-forespørsel
        String postData = "rfid_tag=" + rfidTag;
        client.println("POST /attendance_system/log_attendance.php HTTP/1.1");
        client.println("Host: " + String(serverHost));
        client.println("Content-Type: application/x-www-form-urlencoded");
        client.println("Content-Length: " + String(postData.length()));
        client.println(); // Tom linje før innholdet
        client.println(postData);

        // Les serverens respons
        while (client.connected() || client.available()) {
          if (client.available()) {
            String response = client.readString();
            Serial.println("Server response:");
            Serial.println(response);
            break;
          }
        }

        client.stop();
      } else {
        Serial.println("Failed to connect to server");
      }
    } else {
      Serial.println("WiFi disconnected!");
    }

    // Avslutt kommunikasjon med RFID
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }

  // Håndter forespørsler fra Python GUI(proto)
  WiFiClient client = wifiServer.available();
  if (client) {
    Serial.println("New client connected");

    // Les forespørselen fra klienten
    String request = client.readStringUntil('\r');
    Serial.println(request);

    // Svar med siste RFID
    if (request.indexOf("GET /rfid") != -1) {
      client.println("HTTP/1.1 200 OK");
      client.println("Content-Type: text/plain");
      client.println();
      client.println(lastRFID.isEmpty() ? "Ingen RFID registrert ennå." : "Siste RFID: " + lastRFID);
    }

    // Lukk koblingen
    client.stop();
    Serial.println("Client disconnected");
  }
}
