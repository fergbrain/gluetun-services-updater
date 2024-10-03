# SPDX-FileCopyrightText: Copyright (c) 2024 Andrew Ferguson
#
# SPDX-License-Identifier: MIT

import requests
import os
from utils import log_ip_address

SESSION_COOKIE_FILE = "/data/mam.cookies"  # File location to store the session key


def get_session_cookie_from_file():
    """Read the session cookie from the file."""
    if not os.path.exists(SESSION_COOKIE_FILE):
        return None
    with open(SESSION_COOKIE_FILE, "r") as f:
        return f.read().strip()  # Return cookie as a string (e.g., 'mam_id=SESSION_KEY')


def save_session_cookie_to_file(cookie_jar):
    """Save the session cookies to the file."""
    with open(SESSION_COOKIE_FILE, "w") as f:
        for cookie in cookie_jar:
            f.write(f"{cookie.name}={cookie.value}\n")


def update_mam_session_cookie():
    session_cookie = get_session_cookie_from_file()
    if not session_cookie:
        print("No session cookie found. Logging IP address.")
        log_ip_address()
        return False

    try:
        # Extract the cookie key and value for the request
        cookie_key, cookie_value = session_cookie.split('=')

        # Make the request to update the session cookie
        response = requests.get(
            "https://t.myanonamouse.net/json/dynamicSeedbox.php",
            cookies={cookie_key: cookie_value}
        )

        if response.status_code == 200:
            # Save the updated cookies to the file
            save_session_cookie_to_file(response.cookies)
            print("Session cookie updated successfully.")
            return True
        else:
            print(f"Failed to update session cookie: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error while updating session cookie: {str(e)}")
        return False
