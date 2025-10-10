# backend/api/auth.py
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import logging

from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)

User = get_user_model()

class PhoneBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        phone = username or kwargs.get('phone')
        if not phone or not password:
            return None

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class TokenAndCookieAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token_key = request.COOKIES.get('auth_token') or self.get_token_from_header(request)
        logger.debug(f"Extracted token: {token_key}")

        if not token_key:
            return None

        try:
            user = self.authenticate_credentials(token_key)
            logger.debug(f"Authenticated user: {user}")
        except exceptions.AuthenticationFailed as e:
            logger.warning(f"Authentication failed: {e}")
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

