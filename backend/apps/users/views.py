import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.db import IntegrityError, transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.views import COOKIE_KWARGS, DELETE_COOKIE_KWARGS
from .mail import MailError, notify, send_templated_mail
from .serializers import (
    EMAIL_CHANGE_SALT,
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    ConfirmEmailChangeSerializer,
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

class ConfirmationMailFailed(APIException):
    status_code = 503
    default_detail = 'The confirmation mail could not be sent. Please try again later.'
    default_code = 'confirmation_mail_failed'


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
        transaction.on_commit(lambda: notify(user.email, 'password_changed'))
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
        transaction.on_commit(lambda: notify(user.email, 'password_changed'))
        return Response(status=204)


class ChangeEmailView(APIView):
    """Change the login email. With email configured the new address must confirm first."""
    throttle_scope = 'auth'

    def post(self, request):
        serializer = ChangeEmailSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        new_email = serializer.validated_data['new_email']

        if not settings.EMAIL_ENABLED:
            user.email = new_email
            user.save(update_fields=['email'])
            return Response({'status': 'changed', 'email': new_email})

        token = signing.dumps(
            {'uid': str(user.pk), 'old': user.email, 'new': new_email}, salt=EMAIL_CHANGE_SALT
        )
        url = f'{settings.SITE_URL}/confirm-email/{token}'
        try:
            send_templated_mail(new_email, 'email_change', {'url': url, 'new_email': new_email})
        except MailError:
            raise ConfirmationMailFailed()
        return Response({'status': 'confirmation_sent'}, status=202)


class ConfirmEmailChangeView(APIView):
    """Apply an email change from the link mailed to the new address."""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_scope = 'auth'

    def post(self, request):
        serializer = ConfirmEmailChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        old_email = user.email
        new_email = serializer.validated_data['new_email']

        try:
            with transaction.atomic():
                user.email = new_email
                user.save(update_fields=['email'])
        except IntegrityError:  # someone took the address between validation and save
            return Response({'token': ['This email is already in use.']}, status=400)

        notify(old_email, 'email_changed', {'new_email': new_email})
        return Response({'email': new_email})
