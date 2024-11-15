import requests
from django.conf import settings
from typing import Any


def refresh_firebase_token(refresh_token: str) -> str:
    """
    Refresh the Firebase ID token using a refresh token.

    Args:
        refresh_token (str): The refresh token obtained during initial authentication.

    Returns:
        str: A new Firebase ID token.

    Raises:
        Exception: If the token refresh fails.
    """
    refresh_url = 'https://securetoken.googleapis.com/v1/token'
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    response = requests.post(f'{refresh_url}?key={settings.FIREBASE_API_KEY}', data=payload)

    if response.status_code == 200:
        return response.json()['id_token']
    else:
        error_message = response.json().get('error', {}).get('message', 'Could not refresh token')
        raise Exception(f'Token refresh failed: {error_message}')
