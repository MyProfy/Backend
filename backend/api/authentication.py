from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class TokenAndCookieAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token_key = request.COOKIES.get('auth_token') or self.get_token_from_header(request)

        if not token_key:
            return None
        
        try:
            user, token = self.authenticate_credentials(token_key)
            return (user, token)
        except exceptions.AuthenticationFailed as e:
            raise
    
    def get_token_from_header(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            return auth_header.split(' ')[1]
        return None
    
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')
        
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')
        
        return (token.user, token)
