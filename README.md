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
| `GLUETUN_API_KEY` | _unset_ | API key for gluetun's control server. Sent using the `X-API-Key` header. |
| `QBITTORRENT_URL` | `http://127.0.0.1:8080` | URL to qBittorrent's web UI. |
| `QBITTORRENT_USER` | `admin` | qBittorrent login. |
| `QBITTORRENT_PASSWORD` | `adminadmin` | qBittorrents password. |
| `TIMEOUT` | `3600` | How often port will be changed. |

## Gluetun control server

This updater uses the following endpoints from gluetun's current control API:

- `GET /v1/vpn/status`
- `GET /v1/portforward`

Current gluetun releases require control server authentication by default. Generate
an API key with:

```sh
docker run --rm qmcgaw/gluetun genkey
```

Create a gluetun authentication configuration file containing a role that permits
access to both endpoints:

```toml
[[roles]]
name = "gluetun-services-updater"
routes = [
  "GET /v1/vpn/status",
  "GET /v1/portforward"
]
auth = "apikey"
apikey = "your-generated-api-key"
```

Mount this file into the gluetun container at `/gluetun/auth/config.toml`, then set
`GLUETUN_API_KEY` for this updater to the same value used for `apikey` above.


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
      GLUETUN_API_KEY: ${GLUETUN_API_KEY}
      QBITTORRENT_URL: http://172.18.0.1:8080
    env_file:
      - .env # Contains GLUETUN_API_KEY and QBITTORRENT_PASSWORD
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

