# firebase_setup.py

import firebase_admin
from firebase_admin import credentials
import os
from django.conf import settings

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK using the credentials provided.
    """
    # Path to your Firebase credentials
    cred_path = os.path.join(settings.BASE_DIR, 'config', 'firebase_credentials.json')

    # Check if the credential file exists
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
