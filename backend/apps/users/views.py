from django.db import transaction
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.views import COOKIE_KWARGS, DELETE_COOKIE_KWARGS
from .serializers import ChangePasswordSerializer, UserSerializer
from .tokens import blacklist_all_tokens

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change the password and revoke all sessions except the current device."""
    throttle_scope = 'auth'

    @transaction.atomic
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])

        blacklist_all_tokens(user)
        response = Response(status=204)
        # keep this device logged in with a fresh refresh token
        response.set_cookie('refresh_token', str(RefreshToken.for_user(user)), **COOKIE_KWARGS)
        return response


class LogoutAllView(APIView):
    """Log out everywhere: revoke every refresh token from user."""
    def post(self, request):
        blacklist_all_tokens(request.user)
        response = Response(status=204)
        response.delete_cookie('refresh_token', **DELETE_COOKIE_KWARGS)
        return response
