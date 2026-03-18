# 🛢️ Gas Sensor System (GSS)

A real-time, multi-gas hazard detection and monitoring system built on **ESP32** with **MQ-series sensors**, a full **TICK-stack** data pipeline (Telegraf → InfluxDB → Grafana), and an on-device **Random Forest** classification model — deployable on both Ubuntu and headless **Raspberry Pi** with secure remote access via **Tailscale VPN**.

---

## 📐 System Architecture

```
ESP-32 (MQ-3, MQ-4, MQ-5, MQ-6, MQ-7, MQ-8 + DHT-22 + PM1/2.5/10)
        │  MQTT publish — InfluxDB line protocol
        ▼
Mosquitto MQTT Broker  (port 1883)
        │
        ▼
  Telegraf Agent  ──►  InfluxDB v2  (port 8086)
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
             Grafana Dashboard   InfluxDB Dashboard
               (port 3000)

        ┌──────────────────────────────────┐
        │  ML Classification Model         │
        │  Random Forest — scikit-learn    │
        │  Normal / Dangerous / Recovery   │
        └──────────────────────────────────┘

        ┌──────────────────────────────────┐
        │  Remote Access                   │
        │  Tailscale VPN + Cloudflare Tun  │
        └──────────────────────────────────┘
```

---

## 🔬 Sensors & Detected Gases

| Sensor      | Target Gas(es)                  |
|-------------|---------------------------------|
| MQ-3        | Alcohol / Ethanol               |
| MQ-4        | Methane / Natural Gas           |
| MQ-5        | LPG / Methane / Alcohol         |
| MQ-6        | LPG / Butane                    |
| MQ-7        | Carbon Monoxide (CO)            |
| MQ-8        | Hydrogen (H₂)                   |
| DHT-22      | Temperature & Humidity          |
| PM-1/2.5/10 | Particulate Matter              |

> **14+ hazardous gases** detectable through sensor cross-sensitivity and ML classification.

---

## 📂 Repository Structure

```
GSS/
├── esp32/
│   └── gas_sensor_mqtt/
│       ├── gas_sensor_mqtt.ino   # ESP32 firmware
│       └── config.h              # WiFi / MQTT / pin config
├── telegraf/
│   └── telegraf.conf             # MQTT → InfluxDB pipeline
├── ml/
│   ├── preprocess.py             # Noise filter + normalization
│   ├── train_random_forest.py    # Model training + evaluation
│   ├── predict.py                # Live MQTT inference
│   └── requirements.txt
├── raspberry_pi/
│   └── setup.sh                  # Automated headless RPi setup
├── scripts/
│   └── verify_pipeline.sh        # Service health-check
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SETUP_UBUNTU.md
│   ├── TAILSCALE.md
│   └── CLOUD_COMPARISON.md
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Flash the ESP32

- Open `esp32/gas_sensor_mqtt/gas_sensor_mqtt.ino` in Arduino IDE
- Fill in your credentials in `config.h`
- Install libraries: **PubSubClient**, **DHT sensor library** (Adafruit)
- Flash to your ESP32 board

### 2. Set Up the Data Pipeline

**Ubuntu VM:**
```bash
# Follow docs/SETUP_UBUNTU.md
```

**Headless Raspberry Pi:**
```bash
bash raspberry_pi/setup.sh
```

### 3. Configure Telegraf

```bash
sudo cp telegraf/telegraf.conf /etc/telegraf/telegraf.conf
# Edit YOUR_INFLUXDB_TOKEN_HERE, org, and bucket
sudo systemctl restart telegraf
```

### 4. Open Grafana

Visit `http://localhost:3000` → add InfluxDB as data source → create dashboards.

### 5. Train & Run the ML Model

```bash
cd ml
pip install -r requirements.txt
python train_random_forest.py --data sensor_data.csv
python predict.py   # live inference via MQTT
```

---

## 🌐 Remote Access (Tailscale)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip   # your private VPN IP
```

Access from anywhere:
- Grafana:  `http://<tailscale-ip>:3000`
- InfluxDB: `http://<tailscale-ip>:8086`

See [docs/TAILSCALE.md](docs/TAILSCALE.md) for full setup.

---

## 🔍 Pipeline Health Check

```bash
bash scripts/verify_pipeline.sh
```

---

## 👤 Author

**Vivek Kumar** — Gas Sensor System, 2-Month R&D Project

## 📜 License

MIT License

---

## 📸 Demo

### Hardware + Live System

![GSS Live Demo — ESP32 hardware with live ML classification and Grafana dashboard](assets/images/gss_live_demo.jpeg)

> ESP32 + MQ sensors (red glow) running live, with ML classification output (MQ-5 RECOVERY readings) visible in the terminal and Grafana dashboard open in the browser.

### 🎥 Video Demos

| # | Description | Link |
|---|-------------|------|
| 1 | Full pipeline — MQTT → InfluxDB → Grafana + ML inference | [▶ Watch on YouTube](https://youtu.be/QR55Ek6ZfSA) |
| 2 | Grafana dashboard & real-time sensor data visualization | [▶ Watch on YouTube](https://youtu.be/Rkt77Ig-MbI) |
