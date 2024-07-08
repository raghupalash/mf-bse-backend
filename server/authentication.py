# authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from server.models import UserLoginToken

class BearerTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            user_token = UserLoginToken.objects.get(key=token, is_logged_out=False, is_deleted=False, is_connected=True)
        except UserLoginToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        return (user_token.user, None)