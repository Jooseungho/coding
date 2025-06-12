#include <WiFi.h>
#include "MAX30105.h"
#include "heartRate.h"

// WiFi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const char* serverIP = "192.168.4.2"; // Replace with Python server IP
const uint16_t serverPort = 5000;
const uint16_t SAMPLE_INTERVAL_MS = 20; // 50 Hz

MAX30105 particleSensor;
WiFiClient client;

void setup() {
  Serial.begin(115200);
  delay(100);

  // Initialize MAX30102
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30105 was not found. Please check wiring.");
    while (1);
  }
  particleSensor.setup(); // Configure with default settings

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Connect to server
  while (!client.connect(serverIP, serverPort)) {
    Serial.println("Retrying connection to server...");
    delay(1000);
  }
  Serial.println("Connected to server");
}

void loop() {
  // Read AD8232 analog value
  int ecgValue = analogRead(34); // Use appropriate pin

  // Read MAX30102 values
  uint32_t irValue = particleSensor.getIR();
  uint32_t redValue = particleSensor.getRed();

  // Format CSV string
  String data = String(millis()) + "," + String(ecgValue) + "," + String(irValue) + "," + String(redValue) + "\n";

  // Send to server
  if (client.connected()) {
    client.print(data);
  } else {
    Serial.println("Disconnected from server");
  }

  delay(SAMPLE_INTERVAL_MS); // ~50 Hz sampling rate
}
