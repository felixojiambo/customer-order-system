import firebase_admin
from firebase_admin import credentials
import os
from django.conf import settings

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK using the credentials provided.
    """
    # Path to Firebase credentials within the container
    cred_path = os.path.join(settings.BASE_DIR, '..', 'config', 'firebase', 'firebase_credentials.json')
    cred_path = os.path.abspath(cred_path)  # Ensure it's an absolute path

    # Check if the credential file exists
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
