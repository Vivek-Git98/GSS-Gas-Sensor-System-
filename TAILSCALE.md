# Tailscale VPN Setup — GSS Remote Access

Tailscale creates an encrypted peer-to-peer overlay network (WireGuard-based)
that lets you reach your Grafana, InfluxDB, and MQTT broker from anywhere
without exposing public ports.

## Install on Raspberry Pi / Ubuntu

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Follow the URL printed to authenticate
tailscale ip     # note your assigned VPN IP (e.g. 100.x.y.z)
```

## Install on Client Devices

Download the Tailscale app for your OS/phone and log in with the **same account**.

## Access GSS Services Remotely

| Service   | URL                              |
|-----------|----------------------------------|
| Grafana   | `http://<tailscale-ip>:3000`     |
| InfluxDB  | `http://<tailscale-ip>:8086`     |
| MQTT      | `<tailscale-ip>:1883`            |

## Ensure Tailscale Starts on Boot

```bash
sudo systemctl enable tailscaled
```

## Cloudflare Quick Tunnel (Alternative)

For a lightweight HTTPS tunnel without port forwarding:

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
cloudflared tunnel --url http://localhost:3000
# Cloudflare prints a public HTTPS URL valid for the session
```
