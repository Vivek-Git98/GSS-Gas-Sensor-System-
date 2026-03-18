#!/usr/bin/env bash
# =============================================================
#  GSS — Headless Raspberry Pi Setup Script
#  Installs: Mosquitto, Telegraf, InfluxDB, Grafana, Tailscale
# =============================================================
set -euo pipefail

INFLUXDB_TOKEN="YOUR_INFLUXDB_TOKEN"
INFLUXDB_ORG="your_org"
INFLUXDB_BUCKET="gas_data"
GRAFANA_PORT=3000
INFLUXDB_PORT=8086
MQTT_PORT=1883

echo "============================================"
echo " GSS Raspberry Pi Setup"
echo "============================================"

# ---- System Update ----
echo "[1/7] Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

# ---- Mosquitto MQTT Broker ----
echo "[2/7] Installing Mosquitto..."
sudo apt-get install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
echo "      Mosquitto running on port $MQTT_PORT"

# ---- InfluxDB ----
echo "[3/7] Installing InfluxDB v2..."
curl -s https://repos.influxdata.com/influxdata-archive_compat.key \
  | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' \
  | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt-get update -y
sudo apt-get install -y influxdb2
sudo systemctl enable influxdb
sudo systemctl start influxdb
echo "      InfluxDB running on port $INFLUXDB_PORT"

# ---- Telegraf ----
echo "[4/7] Installing Telegraf..."
sudo apt-get install -y telegraf
sudo cp "$(dirname "$0")/../telegraf/telegraf.conf" /etc/telegraf/telegraf.conf
# Substitute token placeholder
sudo sed -i "s/YOUR_INFLUXDB_TOKEN_HERE/$INFLUXDB_TOKEN/g" /etc/telegraf/telegraf.conf
sudo systemctl enable telegraf
sudo systemctl start telegraf
echo "      Telegraf configured"

# ---- Grafana ----
echo "[5/7] Installing Grafana..."
sudo apt-get install -y apt-transport-https software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update -y
sudo apt-get install -y grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
echo "      Grafana running on port $GRAFANA_PORT"

# ---- Firewall ----
echo "[6/7] Configuring firewall rules..."
sudo ufw allow "$MQTT_PORT/tcp"    comment "Mosquitto MQTT"
sudo ufw allow "$INFLUXDB_PORT/tcp" comment "InfluxDB"
sudo ufw allow "$GRAFANA_PORT/tcp"  comment "Grafana"
sudo ufw --force enable

# ---- Tailscale VPN ----
echo "[7/7] Installing Tailscale VPN..."
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
TAILSCALE_IP=$(tailscale ip 2>/dev/null || echo "<run: tailscale ip>")
echo ""
echo "============================================"
echo " Setup Complete!"
echo "============================================"
echo " Tailscale IP  : $TAILSCALE_IP"
echo " Grafana       : http://$TAILSCALE_IP:$GRAFANA_PORT"
echo " InfluxDB      : http://$TAILSCALE_IP:$INFLUXDB_PORT"
echo " MQTT Broker   : $TAILSCALE_IP:$MQTT_PORT"
echo ""
echo " Next: open InfluxDB UI, create org/bucket,"
echo "       generate a token and update telegraf.conf"
echo "============================================"
