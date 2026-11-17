from datetime import timedelta

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import connection, OperationalError
from django.utils import timezone
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.serializers import RegisterSerializer

User = get_user_model()

COOKIE_KWARGS = dict(
    httponly=True,
    secure=not settings.DEBUG,  # True in production (requires HTTPS)
    samesite='Lax',
    path='/api/token/',
    max_age=int(settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
)
DELETE_COOKIE_KWARGS = dict(path=COOKIE_KWARGS['path'])


class CookieTokenObtainPairView(TokenObtainPairView):
    throttle_scope = 'auth'

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == 200 and 'refresh' in response.data:
            refresh = response.data.pop('refresh')  # don't expose it in JSON
            response.set_cookie('refresh_token', refresh, **COOKIE_KWARGS)
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        # Rotation issues a new refresh token on every refresh: move it to the cookie.
        if response.status_code == 200 and 'refresh' in response.data:
            refresh = response.data.pop('refresh')
            response.set_cookie('refresh_token', refresh, **COOKIE_KWARGS)
        return super().finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'No refresh token cookie'}, status=401)
        request.data['refresh'] = refresh_token
        try:
            return super().post(request, *args, **kwargs)
        except InvalidToken:
            access = self._access_for_recently_rotated(refresh_token)
            if access is None:
                raise
            # No new refresh token: the cookie set by the winning request stays valid.
            return Response({'access': access})

    @staticmethod
    def _access_for_recently_rotated(raw_token):
        """Grace window for a refresh token that was rotated moments ago.

        Rotation blacklists the old token, so two requests racing with the same
        cookie (app update reload, two tabs, a response lost while the page
        unloaded) would log the loser out. Within REFRESH_ROTATION_LEEWAY we
        hand the loser a fresh access token only. Tokens blacklisted by logout
        are never accepted: a rotation always leaves a successor token behind.
        """
        try:
            token = RefreshToken(raw_token, verify=False)
            token.verify_token_type()
            token.check_exp()
            user_id = token[jwt_settings.USER_ID_CLAIM]
            blacklisted = BlacklistedToken.objects.get(token__jti=token[jwt_settings.JTI_CLAIM])
        except (TokenError, KeyError, BlacklistedToken.DoesNotExist):
            return None

        now = timezone.now()
        if now - blacklisted.blacklisted_at > settings.REFRESH_ROTATION_LEEWAY:
            return None

        successor_exists = OutstandingToken.objects.filter(
            user_id=user_id,
            created_at__gte=blacklisted.blacklisted_at - timedelta(seconds=5),
            blacklistedtoken__isnull=True,
        ).exists()
        if not successor_exists:
            return None

        if not User.objects.filter(pk=user_id, is_active=True).exists():
            return None
        return str(token.access_token)


class RegistrationEnabled(permissions.BasePermission):
    message = 'Registration is disabled.'

    def has_permission(self, request, view):
        return settings.REGISTRATION_ENABLED


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny, RegistrationEnabled]
    throttle_scope = 'auth'


class InstanceConfigView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'registration_enabled': settings.REGISTRATION_ENABLED,
            'email_enabled': settings.EMAIL_ENABLED,
            'notice': settings.INSTANCE_NOTICE,
            'extra': settings.INSTANCE_CONFIG_EXTRA,
        })


class HealthView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            connection.ensure_connection()
        except OperationalError:
            return Response({'status': 'error', 'database': 'unavailable'}, status=503)
        return Response({'status': 'ok'})


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response(status=204)
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass  # already expired/blacklisted/invalid: nothing to revoke
        response.delete_cookie('refresh_token', **DELETE_COOKIE_KWARGS)
        return response
