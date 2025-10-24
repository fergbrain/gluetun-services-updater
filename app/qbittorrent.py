# -*- coding: utf-8 -*-
from requests import Session
from requests.exceptions import RequestException

from settings import settings


def login_to_qbittorrent(s: Session) -> None:
    print(f"[qBittorrent] Logging in at {settings.qbittorrent.url}")
    try:
        res = s.post(
            url=f'{settings.qbittorrent.url}/api/v2/auth/login',
            data='username={0.user}&password={0.password}'.format(settings.qbittorrent),
            headers=settings.default_headers,
            timeout=15
        )
    except RequestException as e:
        raise RuntimeError(f"qBittorrent login error: {e.__class__.__name__}: {e}")
    if (code := res.status_code) != 200:
        raise RuntimeError(f'[qBittorrent] Login failed HTTP {code}: {res.text}')
    if not res.cookies.get('SID'):
        raise RuntimeError("[qBittorrent] Login succeeded but no SID cookie (wrong password?)")
    print("[qBittorrent] Login successful")


def update_qbittorrent_port(s: Session, port: int) -> None:
    print(f"[qBittorrent] Setting listen_port to {port}")
    try:
        res = s.post(
            url=f'{settings.qbittorrent.url}/api/v2/app/setPreferences',
            headers=settings.default_headers,
            data='json={"listen_port":' + str(port) + '}',
            timeout=15
        )
    except RequestException as e:
        raise RuntimeError(f"qBittorrent setPreferences error: {e.__class__.__name__}: {e}")
    if (code := res.status_code) != 200:
        raise RuntimeError(f'[qBittorrent] setPreferences failed HTTP {code}: {res.text}')
    print("[qBittorrent] listen_port updated")


def get_qbittorrent_port(session: Session) -> int:
    print("[qBittorrent] Fetching current listen_port")
    try:
        res = session.get(f'{settings.qbittorrent.url}/api/v2/app/preferences', timeout=15)
    except RequestException as e:
        raise RuntimeError(f"qBittorrent get preferences error: {e.__class__.__name__}: {e}")
    if (code := res.status_code) != 200:
        raise RuntimeError(f'[qBittorrent] Get preferences failed HTTP {code}: {res.text}')
    port = int(res.json().get('listen_port'))
    print(f"[qBittorrent] Current listen_port is {port}")
    return port


def verify_qbittorrent_port(session: Session, port: int) -> None:
    actual_port = get_qbittorrent_port(session)
    if actual_port != port:
        raise RuntimeError(f'[qBittorrent] Port mismatch: expected {port}, got {actual_port}')
    print("[qBittorrent] Port verification OK")
