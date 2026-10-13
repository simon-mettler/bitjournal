from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.authentication.views import DELETE_COOKIE_KWARGS
from .serializers import UserSerializer
from .tokens import blacklist_all_tokens

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutAllView(APIView):
    """Log out everywhere: revoke every refresh token from user."""
    def post(self, request):
        blacklist_all_tokens(request.user)
        response = Response(status=204)
        response.delete_cookie('refresh_token', **DELETE_COOKIE_KWARGS)
        return response
