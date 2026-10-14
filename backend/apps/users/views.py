import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.views import COOKIE_KWARGS, DELETE_COOKIE_KWARGS
from .mail import MailError, send_templated_mail
from .serializers import (
    ChangePasswordSerializer,
    DeleteAccountSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserSerializer,
)
from .signals import account_deleting
from .tokens import blacklist_all_tokens

logger = logging.getLogger(__name__)

User = get_user_model()


class AccountDeletionFailed(APIException):
    status_code = 503
    default_detail = 'Your account could not be deleted. Nothing was removed, please try again later.'
    default_code = 'account_deletion_failed'

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


class DeleteAccountView(APIView):
    """Permanently delete the account and all its data."""
    throttle_scope = 'auth'

    @transaction.atomic
    def post(self, request):
        serializer = DeleteAccountSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        try:
            account_deleting.send(sender=type(user), user=user)
        except Exception:
            logger.exception('account_deleting receiver failed for user %s', user.pk)
            raise AccountDeletionFailed()

        blacklist_all_tokens(user)
        user.delete()  # cascades to signals, boards, events, analytics

        response = Response(status=204)
        response.delete_cookie('refresh_token', **DELETE_COOKIE_KWARGS)
        return response


class EmailEnabled(permissions.BasePermission):
    message = 'Email is not configured on this instance.'

    def has_permission(self, request, view):
        return settings.EMAIL_ENABLED


class PasswordResetRequestView(APIView):
    """Send a reset link."""
    permission_classes = [permissions.AllowAny, EmailEnabled]
    authentication_classes = []
    throttle_scope = 'auth'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email__iexact=serializer.validated_data['email'], is_active=True
        ).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            url = f'{settings.SITE_URL}/reset-password/{uid}/{token}'
            try:
                send_templated_mail(user.email, 'password_reset', {'url': url})
            except MailError:
                pass  # already logged; the caller must not learn whether the user exists
        return Response(status=204)


class PasswordResetConfirmView(APIView):
    """Set a new password with the uid/token from the reset mail."""
    permission_classes = [permissions.AllowAny, EmailEnabled]
    authentication_classes = []
    throttle_scope = 'auth'

    @transaction.atomic
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])  # also invalidates the reset token
        blacklist_all_tokens(user)
        return Response(status=204)
