# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: Copyright (c) 2024 Jakub Suchenek
# SPDX-FileCopyrightText: Copyright (c) 2024 Andrew Ferguson
#
# SPDX-License-Identifier: MIT
import requests

from settings import settings


def sep(text: str, *, n: int = 4, char: str = '*') -> None:
    print('\n{0} {1} {0}'.format(n * char, text))

def log_ip_address():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            ip_data = response.json()
            print(f"Current IP Address: {ip_data['ip']}")
        else:
            print(f"Failed to get IP address: {response.status_code}")
    except Exception as e:
        print(f"Error while logging IP address: {str(e)}")


def write_health_status(status):
    """Write the container's health status to a file."""
    with open(settings.healthstatusfile, "w") as f:
        f.write(status)
