from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from .models import User

class FirebaseAuthentication(BaseAuthentication):
    """
    Custom authentication class to authenticate users using Firebase ID tokens.
    """
    def authenticate(self, request):
        """
        Authenticate the request using the Firebase ID token.
        """
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None

        try:
            token = token.split(' ')[1]
        except IndexError:
            raise AuthenticationFailed('Invalid token header. No token provided.')

        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']

            user = User.objects.get(uid=uid)
            return (user, token)
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError, User.DoesNotExist) as e:
            raise AuthenticationFailed(str(e))
        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

        return None
