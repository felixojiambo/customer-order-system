import requests
from django.conf import settings

def refresh_firebase_token(refresh_token):
    """
    Refresh the Firebase ID token using a refresh token.
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
        raise Exception('Could not refresh token')
