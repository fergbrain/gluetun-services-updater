# qbt-updater-for-gluetun

Updater for services that use gluetun, such as qBittorrent and myAnonymouse.

## Running directly

```sh
python app/main.py
```

## Available environment variables

| Name |  Default value | Description |
| --- |  --- | --- |
| `GLUETUN_URL` | `http://127.0.0.1:8000` | URL to gluetun's control server. |
| `QBITTORRENT_URL` | `http://127.0.0.1:8080` | URL to qBittorrent's web UI. |
| `QBITTORRENT_USER` | `admin` | qBittorrent login. |
| `QBITTORRENT_PASSWORD` | `adminadmin` | qBittorrents password. |
| `TIMEOUT` | `3600` | How often port will be changed. |


## Running in Docker Compose

```yaml
---
services:
  qbt-updater:
    build: https://github.com/fergbrain/gluetun-services-updater.git#main
    container_name: gluetun-updater
    restart: unless-stopped
    environment:
      # Assuming apps expose ports on gateway of "custom-network"
      # Note: without Docker DNS tricks, hostnames are unsopported
      GLUETUN_URL: http://172.18.0.1:8000
      QBITTORRENT_URL: http://172.18.0.1:8080
    env_file:
      - .env # Contains QBITTORRENT_PASSWORD
    volumes:
      - ./data:/data  # Mount the data directory to persist cookies
    networks:
      - custom-network # Must be the same as gluetun and qBittorrent
    healthcheck:
      test: ["CMD", "cat", "/data/health_status.txt", "|", "grep", "'healthy'"]
      interval: 5m  # How often to run the check
      timeout: 30s  # Timeout before assuming the script failed
      retries: 3  # Number of retries before marking the container as unhealthy
      start_period: 30s  # Initial delay before starting health checks


networks:
  custom-network:
    external: true
```

