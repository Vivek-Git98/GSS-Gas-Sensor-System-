# GSS — Architecture & Data Flow

## Full Pipeline

```
┌──────────────────────────────────────────────────────┐
│                      ESP-32                          │
│   MQ-3  MQ-4  MQ-5  MQ-6  MQ-7  MQ-8               │
│   DHT-22  PM-1  PM-2.5  PM-10                        │
│                                                      │
│   analogRead() → voltage conversion                  │
│   Build InfluxDB line-protocol string                │
│   WiFi → MQTT publish @ gas_sensors/lab             │
└────────────────────────┬─────────────────────────────┘
                         │ MQTT (port 1883)
                         ▼
            ┌────────────────────────┐
            │   Mosquitto MQTT Broker│
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │       Telegraf         │
            │  inputs.mqtt_consumer  │
            │  outputs.influxdb_v2   │
            └────────────┬───────────┘
                         │ HTTP (port 8086)
                         ▼
            ┌────────────────────────┐
            │      InfluxDB v2       │
            │   bucket: gas_data     │
            └────────┬──────┬────────┘
                     │      │
          ┌──────────▼──┐ ┌─▼──────────────────────┐
          │   Grafana   │ │  Random Forest Model    │
          │  Dashboard  │ │  Normal / Dangerous /   │
          │  :3000      │ │  Recovery               │
          └─────────────┘ └────────────────────────┘

            ┌────────────────────────────────────┐
            │        Remote Access               │
            │  Tailscale VPN  (WireGuard)        │
            │  Cloudflare Tunnel  (optional)     │
            └────────────────────────────────────┘
```

## ML Classification

| Step | Detail |
|------|--------|
| Data collection | Labelled CSV exported from InfluxDB |
| Preprocessing | Rolling-median noise filter → MinMax normalization |
| Training | Random Forest (scikit-learn), optional GridSearchCV |
| Inference | `predict.py` subscribes to MQTT and classifies live |
| Alert output | Colour-coded console: green / yellow / red |

## Flag System

| Class     | Meaning                                 |
|-----------|-----------------------------------------|
| Normal    | Safe atmospheric conditions             |
| Dangerous | Hazardous gas concentration detected   |
| Recovery  | Transitional / alert clearing phase    |
