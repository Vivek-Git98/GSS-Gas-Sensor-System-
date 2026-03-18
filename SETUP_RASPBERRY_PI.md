# Headless Raspberry Pi Setup — GSS

## 1. Flash Raspberry Pi OS (Headless)

Use **Raspberry Pi Imager** on your PC:
- OS: Raspberry Pi OS Lite (64-bit)
- Enable SSH, set hostname, Wi-Fi credentials in the imager settings before flashing.

## 2. First SSH Login

```bash
ssh pi@<raspberry-pi-ip>
```

## 3. Run Automated Setup

```bash
git clone https://github.com/<your-username>/GSS.git
cd GSS
chmod +x raspberry_pi/setup.sh
bash raspberry_pi/setup.sh
```

This installs: Mosquitto, InfluxDB, Telegraf, Grafana, Tailscale.

## 4. Complete InfluxDB Setup

Open `http://<pi-ip>:8086` from another device on the same network:
- Create organization and bucket (`gas_data`)
- Generate an API token
- Paste token into `/etc/telegraf/telegraf.conf` and restart Telegraf

## 5. Configure Telegraf Token

```bash
sudo nano /etc/telegraf/telegraf.conf
# Replace YOUR_INFLUXDB_TOKEN_HERE with your actual token
sudo systemctl restart telegraf
```

## 6. Verify Everything

```bash
bash scripts/verify_pipeline.sh
```

## 7. Remote Access via Tailscale

```bash
sudo tailscale up    # follow printed URL to authenticate
tailscale ip         # note your Tailscale IP
```

Services are now accessible from anywhere:
- `http://<tailscale-ip>:3000` — Grafana
- `http://<tailscale-ip>:8086` — InfluxDB
