import firebase_admin
from firebase_admin import credentials
import os
from django.conf import settings


def initialize_firebase():
    """
    Initializes the Firebase Admin SDK using the credentials provided.

    - Uses a specified path for the Firebase credentials JSON file.
    - Raises an error if the credentials file is missing, ensuring Firebase is not initialized without proper credentials.
    """
    # Construct the absolute path to the Firebase credentials JSON file
    cred_path = os.path.join(settings.BASE_DIR, '..', 'config', 'firebase', 'firebase_credentials.json')
    cred_path = os.path.abspath(cred_path)  # Ensure the path is absolute

    # Check if the Firebase credentials file exists
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")

    # Load and initialize Firebase Admin with the provided credentials
    cred = credentials.Certificate(cred_path)
    if not firebase_admin._apps:  # Check if Firebase is already initialized
        firebase_admin.initialize_app(cred)
