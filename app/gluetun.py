# -*- coding: utf-8 -*-
from requests import Session
from requests.exceptions import RequestException

from time import sleep

from settings import settings


def _headers() -> dict:
    """Return headers required by Gluetun's control server."""
    if settings.gluetun.api_key:
        return {
            'X-API-Key': settings.gluetun.api_key
        }
    return {}


def is_gluetun_ready(s: Session) -> bool:
    try:
        url = f'{settings.gluetun.url}/v1/vpn/status'
        print(f"[gluetun] Checking status at {url}")

        res = s.get(
            url,
            headers=_headers(),
            timeout=10
        )

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
            print(
                f"[gluetun] HTTP {code} from status endpoint: "
                f"{res.text.strip()!r}; retrying in 5s"
            )

        sleep(5.0)
        return False

    except RequestException as e:
        print(
            f"[gluetun] Status check error: "
            f"{e.__class__.__name__}: {e} — retrying in 5s"
        )
        sleep(5.0)
        return False


def get_assigned_port(s: Session) -> int:
    backoff = 2.0
    tries = 6

    url = f'{settings.gluetun.url}/v1/portforward'

    for attempt in range(1, tries + 1):
        print(
            f"[gluetun] Fetching forwarded port "
            f"(attempt {attempt}/{tries})"
        )

        try:
            res = s.get(
                url,
                headers=_headers(),
                timeout=10
            )

            if res.status_code == 200:
                try:
                    port = int(res.json().get('port'))
                    print(f"[gluetun] Received forwarded port: {port}")
                    return port
                except (ValueError, TypeError):
                    print(
                        "[gluetun] Malformed response JSON; retrying"
                    )
            else:
                print(
                    f"[gluetun] HTTP {res.status_code} "
                    f"from portforward endpoint: "
                    f"{res.text.strip()!r}; retrying"
                )

        except RequestException as e:
            print(
                f"[gluetun] Error fetching forwarded port: "
                f"{e.__class__.__name__}: {e}"
            )

        print(
            f"[gluetun] Backing off {backoff:.1f}s before retry"
        )
        sleep(backoff)
        backoff = min(backoff * 2, 32.0)

    print(
        "[gluetun] Final attempt to retrieve forwarded port "
        "before failing"
    )

    res = s.get(
        url,
        headers=_headers(),
        timeout=10
    )

    code = res.status_code
    text = res.text

    raise RuntimeError(
        f'Error retrieving forwarded port. '
        f'Last status {code}: {text}'
    )