#!/usr/bin/env bash
# =============================================================
#  verify_pipeline.sh — GSS Service Health Check
#  Verifies Mosquitto, InfluxDB, Telegraf, and Grafana are up
# =============================================================
set -uo pipefail

GREEN="\033[92m"
RED="\033[91m"
YELLOW="\033[93m"
RESET="\033[0m"

PASS=0; FAIL=0

check_service() {
  local name="$1"
  if systemctl is-active --quiet "$name"; then
    echo -e "  ${GREEN}✔ ${name}${RESET} is running"
    ((PASS++))
  else
    echo -e "  ${RED}✗ ${name}${RESET} is NOT running — try: sudo systemctl start $name"
    ((FAIL++))
  fi
}

check_port() {
  local name="$1"; local port="$2"
  if nc -z localhost "$port" 2>/dev/null; then
    echo -e "  ${GREEN}✔ ${name}${RESET} listening on :$port"
  else
    echo -e "  ${YELLOW}⚠ ${name}${RESET} not reachable on :$port"
  fi
}

echo "========================================"
echo " GSS Pipeline Health Check"
echo "========================================"

echo ""
echo "── Services ─────────────────────────────"
check_service "mosquitto"
check_service "influxdb"
check_service "telegraf"
check_service "grafana-server"

echo ""
echo "── Ports ────────────────────────────────"
check_port "MQTT"     1883
check_port "InfluxDB" 8086
check_port "Grafana"  3000

echo ""
echo "── MQTT Test Publish ────────────────────"
TEST_PAYLOAD='gas_sensors,location=lab,device=test mq3_v=1.2,mq4_v=0.8,mq5_v=1.0,mq6_v=0.9,mq7_v=0.5,mq8_v=0.4,temp=25.0,humidity=55.0'
if mosquitto_pub -h localhost -t "gas_sensors/lab" -m "$TEST_PAYLOAD" 2>/dev/null; then
  echo -e "  ${GREEN}✔ Test message published to MQTT${RESET}"
else
  echo -e "  ${RED}✗ MQTT publish failed${RESET}"
fi

echo ""
echo "========================================"
echo " Results: ${PASS} passed, ${FAIL} failed"
echo "========================================"
