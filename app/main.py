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
from utils import sep

from myanonamouse import update_mam_session_cookie


def main():
    # gluetun
    try:
        with Session() as s:
            sep('gluetun')

            # Wait for gluetun
            while not is_gluetun_ready(s):
                print('Waiting for gluetun...')
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
            print('Trying to login to qBittorrent...')
            login_to_qbittorrent(s)
            print('Logged in')

            # Update listening port
            print('Trying to update listening port...')
            update_qbittorrent_port(s, port)
            print('Port updated')

            # Verify if port has been changed (for my sanity)
            print('Verifying port...')
            verify_qbittorrent_port(s, port)
            print('Port verified')
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
            print("Session cookie is up-to-date.")
        else:
            print("Session cookie update failed. Please verify the session cookie.")

    except Exception as e:
        raise e

    sep('Done')
    print(f'Next run in {settings.timeout} seconds...')
    sleep(settings.timeout)


if __name__ == '__main__':
    try:
        while True:
            main()
    except Exception as e:
        print(f'{e.__class__.__name__}: {e}')
    except KeyboardInterrupt:
        exit()
