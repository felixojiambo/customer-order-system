from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from app.customerorder.models import User
from typing import Optional, Tuple


class FirebaseAuthentication(BaseAuthentication):
    """
    Custom authentication class to authenticate users using Firebase ID tokens.
    """
    def authenticate(self, request) -> Optional[Tuple[User, str]]:
        """
        Authenticate the request using the Firebase ID token.

        Args:
            request: The HTTP request containing the token.

        Returns:
            Optional[Tuple[User, str]]: A tuple of the authenticated user and the token, or None if authentication fails.

        Raises:
            AuthenticationFailed: If authentication fails due to an invalid, expired, or revoked token.
        """
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None

        try:
            # Extract the actual token from the "Bearer <token>" format
            token = token.split(' ')[1]
        except IndexError:
            raise AuthenticationFailed('Invalid token header. No token provided.')

        try:
            # Verify the token with Firebase and retrieve the UID
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']

            # Retrieve the corresponding user from the local database
            user = User.objects.get(uid=uid)
            return (user, token)

        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError, User.DoesNotExist) as e:
            raise AuthenticationFailed(f"Authentication failed: {str(e)}")
        except Exception as e:
            raise AuthenticationFailed(f"Authentication error: {str(e)}")

        return None
