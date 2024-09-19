# -*- coding: utf-8 -*-
import requests
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