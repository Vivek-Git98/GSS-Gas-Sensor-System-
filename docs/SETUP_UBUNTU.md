# Ubuntu Setup Guide — GSS Pipeline

Tested on Ubuntu 22.04 LTS inside a VM or bare-metal.

## 1. System Update

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

## 2. Mosquitto MQTT Broker

```bash
sudo apt-get install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto && sudo systemctl start mosquitto
# Test:
mosquitto_pub -h localhost -t test -m "hello"
```

## 3. InfluxDB v2

```bash
curl -s https://repos.influxdata.com/influxdata-archive_compat.key \
  | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' \
  | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt-get update && sudo apt-get install -y influxdb2
sudo systemctl enable influxdb && sudo systemctl start influxdb
```

Open `http://localhost:8086` → complete setup wizard → create **org**, **bucket** (`gas_data`), and an **API token**.

## 4. Telegraf

```bash
sudo apt-get install -y telegraf
sudo cp telegraf/telegraf.conf /etc/telegraf/telegraf.conf
# Edit token, org, bucket in the file:
sudo nano /etc/telegraf/telegraf.conf
sudo systemctl enable telegraf && sudo systemctl start telegraf
```

## 5. Grafana

```bash
sudo apt-get install -y apt-transport-https software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update && sudo apt-get install -y grafana
sudo systemctl enable grafana-server && sudo systemctl start grafana-server
```

Open `http://localhost:3000` (default login: `admin` / `admin`).  
Add InfluxDB as a data source → create dashboards.

## 6. Firewall

```bash
sudo ufw allow 1883/tcp   # MQTT
sudo ufw allow 8086/tcp   # InfluxDB
sudo ufw allow 3000/tcp   # Grafana
sudo ufw enable
```

## 7. Verify Everything

```bash
bash scripts/verify_pipeline.sh
```
