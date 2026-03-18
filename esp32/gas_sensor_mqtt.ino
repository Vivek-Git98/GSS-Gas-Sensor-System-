/**
 * Gas Sensor System (GSS) — ESP32 Firmware
 * ==========================================
 * Reads MQ-3, MQ-4, MQ-5, MQ-6, MQ-7, MQ-8, DHT-22, and
 * PM sensors then publishes data via MQTT to a Mosquitto broker
 * in InfluxDB line-protocol format for direct Telegraf ingestion.
 *
 * Dependencies (install via Arduino Library Manager):
 *   - PubSubClient  by Nick O'Leary
 *   - DHT sensor library by Adafruit
 *   - Adafruit Unified Sensor
 *
 * Author : Vivek Kumar
 * Board  : ESP32 (DOIT ESP32 DevKit or equivalent)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "config.h"

// ---- Objects ----
DHT       dht(DHT_PIN, DHT_TYPE);
WiFiClient  espClient;
PubSubClient mqttClient(espClient);

// =============================================
//  Wi-Fi Setup
// =============================================
void setupWiFi() {
  Serial.print("[WiFi] Connecting to ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("[WiFi] Connected. IP: ");
  Serial.println(WiFi.localIP());
}

// =============================================
//  MQTT Reconnect
// =============================================
void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Connecting...");
    if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)) {
      Serial.println(" connected.");
    } else {
      Serial.print(" failed (rc=");
      Serial.print(mqttClient.state());
      Serial.println("). Retrying in 5s...");
      delay(5000);
    }
  }
}

// =============================================
//  Inbound Command Handler (optional)
// =============================================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  Serial.print("[MQTT] Message on ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(msg);
  // Add command handling logic here if needed
}

// =============================================
//  Arduino Setup
// =============================================
void setup() {
  Serial.begin(115200);
  delay(500);

  // Pin modes
  pinMode(MQ3_PIN, INPUT);
  pinMode(MQ4_PIN, INPUT);
  pinMode(MQ5_PIN, INPUT);
  pinMode(MQ6_PIN, INPUT);
  pinMode(MQ7_PIN, INPUT);
  pinMode(MQ8_PIN, INPUT);

  dht.begin();
  setupWiFi();

  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(512);  // InfluxDB line-protocol payload can be large
}

// =============================================
//  Helper: ADC raw → Voltage
// =============================================
float toVoltage(int raw) {
  return raw * (ADC_VREF / ADC_MAX);
}

// =============================================
//  Build InfluxDB Line-Protocol Payload
// =============================================
String buildPayload() {
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  float mq3 = toVoltage(analogRead(MQ3_PIN));
  float mq4 = toVoltage(analogRead(MQ4_PIN));
  float mq5 = toVoltage(analogRead(MQ5_PIN));
  float mq6 = toVoltage(analogRead(MQ6_PIN));
  float mq7 = toVoltage(analogRead(MQ7_PIN));
  float mq8 = toVoltage(analogRead(MQ8_PIN));

  // InfluxDB line protocol:
  // measurement,tag_key=tag_val field_key=val[,field_key=val...] timestamp
  String payload = "gas_sensors,location=lab,device=esp32 ";
  payload += "temp=" + String(temp, 2) + ",";
  payload += "humidity=" + String(hum, 2) + ",";
  payload += "mq3_v=" + String(mq3, 4) + ",";
  payload += "mq4_v=" + String(mq4, 4) + ",";
  payload += "mq5_v=" + String(mq5, 4) + ",";
  payload += "mq6_v=" + String(mq6, 4) + ",";
  payload += "mq7_v=" + String(mq7, 4) + ",";
  payload += "mq8_v=" + String(mq8, 4);
  // Telegraf will add the timestamp when it ingests from MQTT

  return payload;
}

// =============================================
//  Arduino Loop
// =============================================
void loop() {
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  String payload = buildPayload();
  Serial.println("[Publish] " + payload);

  if (!mqttClient.publish(MQTT_TOPIC, payload.c_str())) {
    Serial.println("[MQTT] Publish failed. Check broker connection.");
  }

  delay(PUBLISH_INTERVAL_MS);
}
