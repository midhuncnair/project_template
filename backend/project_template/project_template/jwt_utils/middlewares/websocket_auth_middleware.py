#! /usr/bin/env python
"""websocket middleware
"""


__all__ = [
    'JwtAuthMiddlewareStack',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import logging

from urllib.parse import parse_qs

from django.contrib.auth import get_user_model
# from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
# from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
    TokenError,
)
from rest_framework_simplejwt.settings import api_settings
# from rest_framework_simplejwt.tokens import UntypedToken
# from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.state import User

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack

# from jwt import decode as jwt_decode


logger = logging.getLogger(__name__)
User = get_user_model()
AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES


@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token[api_settings.USER_ID_CLAIM]
    except KeyError:
        raise InvalidToken(_("Token contained no recognizable user identification"))

    try:
        user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
    except User.DoesNotExist:
        raise AuthenticationFailed(_("User not found"), code="user_not_found")

    if not user.is_active:
        raise AuthenticationFailed(_("User is inactive"), code="user_inactive")

    return user


class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def get_header(self, scope):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = scope["query_string"]
        if hasattr(header, 'decode'):
            header = scope["query_string"].decode("utf8")

        return header

    async def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        header_dict = parse_qs(header)

        token_key = None
        for k in AUTH_HEADER_TYPES:
            if k in header_dict and header_dict[k] is not None:
                token_key = k
                break

        if token_key is None:
            # Empty AUTHORIZATION header sent
            # Assume the header does not contain a JSON web token
            return None

        return header_dict[token_key][0]

    async def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidToken(
            {
                "detail": _("Given token not valid for any token type"),
                "messages": messages,
            }
        )

    async def authenticate(self, scope):
        header = await self.get_header(scope)
        if header is None:
            return None

        raw_token = await self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = await self.get_validated_token(raw_token)

        return await self.get_user(validated_token), validated_token

    async def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        return await get_user(validated_token)

    async def __call__(self, scope, receive, send):
       # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        try:
            user, validated_token = await self.authenticate(scope)
        except Exception as err:
            logger.critical(
                "Error while authenticating in ws and is %s:%s",
                err.__class__.__name__,
                str(err)
            )
            return None
        else:
            scope["user"] = user
            print("the validated token is = ", validated_token)

        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))
