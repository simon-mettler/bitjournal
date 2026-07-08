from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.users.serializers import UserSerializer

User = get_user_model()

COOKIE_KWARGS = dict(
    httponly=True,
    secure=not settings.DEBUG,  # True in production (requires HTTPS)
    samesite='Lax',
    path='/api/token/',
)


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == 200 and 'refresh' in response.data:
            refresh = response.data.pop('refresh')  # don't expose it in JSON
            response.set_cookie('refresh_token', refresh, **COOKIE_KWARGS)
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'No refresh token cookie'}, status=401)
        request.data['refresh'] = refresh_token
        return super().post(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response(status=204)
        response.delete_cookie('refresh_token', path='/api/token/')
        return response
