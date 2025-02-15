#include <Wire.h>
// #include <MPU6050.h> // Acceleromenter/gyro
#include <Adafruit_MPU6050.h>
#include <SPI.h>
#include <MFRC522.h> // RFID Reader

#define SS_PIN 10
#define RST_PIN 9
MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance

const int TILT_PIN = 2; // Tilt sensor pin
int ledPin = 5;
int sensorPin = 4;
bool lastTiltState = false; // Previous reading from the tilt sensor
unsigned long lastRFIDTime = 0; // Time of the last RFID card scan
bool printedEmpty = false; // Flag to track if "EMPTY" has been printed
bool firstScan = true; // Flag to check if it's the first scan

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(9600); // Initialize serial communication
  SPI.begin(); // Initialize SPI communication
  mfrc522.PCD_Init(); // Initialize MFRC522
  pinMode(TILT_PIN, INPUT_PULLUP); // Set TILT_PIN as an input with an internal pull-up resistor
  pinMode(ledPin, OUTPUT);
  pinMode(sensorPin, INPUT);
  digitalWrite(sensorPin, HIGH);
  Wire.begin();

  // Try to initialize!
  if (!mpu.begin()) {
    // Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  // Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  // mpu.setFilterBandwidth(MPU6050_BAND_5_HZ);
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  // Check for new RFID card every 800 milliseconds
  if (mfrc522.PICC_IsNewCardPresent()) {
    // Select one of the cards
    if (mfrc522.PICC_ReadCardSerial()) {
      // Print the serial number of the RFID card
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
        Serial.print(mfrc522.uid.uidByte[i], HEX);
      }

      Serial.print("|");
      Serial.print(a.acceleration.x);
      Serial.print("|");
      Serial.print(a.acceleration.y);
      Serial.print("|");
      Serial.print(a.acceleration.z);
      // Check y-coordinate range and print appropriate label
      // if (ay >= -9000 && ay <= 9000) {
      //   // Serial.print(" 0");
      //   true;
      // } else if ((ay >= -18000 && ay <= -9001) || (ay >= 9001 && ay <= 18000)) {
      //   // Serial.print(" 1");
      //   true;
      // }

      Serial.println(); // Move to the next line

      // lastRFIDTime = millis(); // Update the last RFID card scan time
      // printedEmpty = false; // Reset the "EMPTY" flag
      // firstScan = false; // Set the "firstScan" flag to false
      delay(10);
    }
  }

  // No longer checking and printing "EMPTY" part

  delay(20);
}