from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import connection, OperationalError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.serializers import UserSerializer

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
        return super().post(request, *args, **kwargs)


class RegistrationEnabled(permissions.BasePermission):
    message = 'Registration is disabled.'

    def has_permission(self, request, view):
        return settings.REGISTRATION_ENABLED


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
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
