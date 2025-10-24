# -*- coding: utf-8 -*-
from requests import Session
from requests.exceptions import RequestException

from time import sleep

from settings import settings


def is_gluetun_ready(s: Session) -> bool:
    try:
        print(f"[gluetun] Checking status at {settings.gluetun.url}/v1/openvpn/status")
        res = s.get(f'{settings.gluetun.url}/v1/openvpn/status', timeout=10)
        if (code := res.status_code) == 200:
            try:
                status = res.json().get('status')
            except ValueError:
                status = None
            if status == 'running':
                print("[gluetun] Status is running")
                return True
            print(f"[gluetun] Status is '{status}', retrying in 5s")
        else:
            print(f"[gluetun] HTTP {code} from status endpoint, retrying in 5s")
        sleep(5.0)
        return False
    except RequestException as e:
        # Connection not ready (e.g., refused, timeout). Retry after delay.
        print(f"[gluetun] Status check error: {e.__class__.__name__}: {e} — retrying in 5s")
        sleep(5.0)
        return False


def get_assigned_port(s: Session) -> int:
    # Retry guard: attempt a few times before failing hard
    backoff = 2.0
    tries = 6  # ~1+2+4+8+16+32 = ~63s worst-case
    for attempt in range(1, tries + 1):
        print(f"[gluetun] Fetching forwarded port (attempt {attempt}/{tries})")
        try:
            res = s.get(f'{settings.gluetun.url}/v1/openvpn/portforwarded', timeout=10)
            if res.status_code == 200:
                try:
                    port = int(res.json().get('port'))
                    print(f"[gluetun] Received forwarded port: {port}")
                    return port
                except (ValueError, TypeError):
                    print("[gluetun] Malformed response JSON; retrying")
            else:
                print(f"[gluetun] HTTP {res.status_code} from portforwarded endpoint; retrying")
        except RequestException as e:
            # Connection errors/timeouts; fall through to retry
            print(f"[gluetun] Error fetching forwarded port: {e.__class__.__name__}: {e}")

        # Backoff before next try
        print(f"[gluetun] Backing off {backoff:.1f}s before retry")
        sleep(backoff)
        backoff = min(backoff * 2, 32.0)

    # After retries, fetch one last time to surface an actionable error
    print("[gluetun] Final attempt to retrieve forwarded port before failing")
    res = s.get(f'{settings.gluetun.url}/v1/openvpn/portforwarded', timeout=10)
    code = res.status_code
    text = res.text
    raise RuntimeError(f'Error retrieving forwarded port. Last status {code}: {text}')
