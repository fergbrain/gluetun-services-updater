# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: Copyright (c) 2024 Jakub Suchenek
# SPDX-FileCopyrightText: Copyright (c) 2024 Andrew Ferguson
#
# SPDX-License-Identifier: MIT
from requests import Session

from time import sleep

from gluetun import is_gluetun_ready, get_assigned_port
from qbittorrent import login_to_qbittorrent, update_qbittorrent_port, \
    verify_qbittorrent_port
from settings import settings
from utils import sep, write_health_status

from myanonamouse import update_mam_session_cookie


def main():
    print(f"[config] GLUETUN_URL={settings.gluetun.url}")
    print(f"[config] QBITTORRENT_URL={settings.qbittorrent.url}")
    print(f"[config] Run interval={int(settings.timeout)}s")
    # gluetun
    try:
        with Session() as s:
            sep('gluetun')

            # Wait for gluetun
            while not is_gluetun_ready(s):
                print('[gluetun] Waiting for service to be ready...')
            print('Gluetun is running')

            # Get assigned port
            port = get_assigned_port(s)
            print(f'Assigned port: {port}')
    except Exception as e:
        raise e
    finally:
        s.close()

    # qBittorrent
    try:
        with Session() as s:
            sep('qBittorrent')

            # Login to qBittorent
            print('[qBittorrent] Trying to login...')
            login_to_qbittorrent(s)
            print('[qBittorrent] Logged in')

            # Update listening port
            print('[qBittorrent] Trying to update listening port...')
            update_qbittorrent_port(s, port)
            print('[qBittorrent] Port updated')

            # Verify if port has been changed (for my sanity)
            print('[qBittorrent] Verifying port...')
            verify_qbittorrent_port(s, port)
            print('[qBittorrent] Port verified')
    except Exception as e:
        raise e
    finally:
        s.close()

    # myAnonamouse
    try:
        sep('myAnonamouse')
        # Periodically check and update the session key
        session_updated = update_mam_session_cookie()
        if session_updated:
            print("[myAnonamouse] Session cookie is up-to-date.")
            write_health_status("healthy")  # Mark as healthy if successful
        else:
            print("[myAnonamouse] Session cookie update failed. Please verify the session cookie.")
            write_health_status("unhealthy")  # Mark as unhealthy on exception


    except Exception as e:
        raise e

    sep('Done')
    print(f'Next run in {settings.timeout} seconds...')
    sleep(settings.timeout)


if __name__ == '__main__':
    retry_delay = 2.0
    max_retry_delay = 60.0
    while True:
        try:
            main()
            retry_delay = 2.0
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(f'{e.__class__.__name__}: {e}')
            write_health_status("unhealthy")
            print(f'[retry] Retrying in {retry_delay:.0f} seconds...')
            sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_retry_delay)
