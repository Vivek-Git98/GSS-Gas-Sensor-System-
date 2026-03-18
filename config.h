#ifndef CONFIG_H
#define CONFIG_H

// =============================================
//  Wi-Fi Credentials
// =============================================
#define WIFI_SSID     "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// =============================================
//  MQTT Broker Settings
// =============================================
#define MQTT_SERVER   "192.168.1.100"   // IP of your Mosquitto broker
#define MQTT_PORT     1883
#define MQTT_USER     ""                // Leave empty if no auth
#define MQTT_PASSWORD ""
#define MQTT_TOPIC    "gas_sensors/lab"
#define MQTT_CLIENT_ID "ESP32_GSS"

// =============================================
//  Sensor GPIO Pins
// =============================================
#define DHT_PIN   4
#define DHT_TYPE  DHT22

#define MQ3_PIN   32
#define MQ4_PIN   33
#define MQ5_PIN   25
#define MQ6_PIN   26
#define MQ7_PIN   27
#define MQ8_PIN   14

// PM sensor UART
#define PM_RX_PIN 16
#define PM_TX_PIN 17

// =============================================
//  Sampling Interval (milliseconds)
// =============================================
#define PUBLISH_INTERVAL_MS 10000   // 10 seconds

// =============================================
//  ADC Reference Voltage
// =============================================
#define ADC_MAX   4095.0f
#define ADC_VREF  3.3f

#endif // CONFIG_H
