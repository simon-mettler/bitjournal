from django.urls import path
from .views import (
    ChangeEmailView,
    ChangePasswordView,
    ConfirmEmailChangeView,
    DeleteAccountView,
    LogoutAllView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
)

urlpatterns = [
    path('users/me/', MeView.as_view()),
    path('users/me/password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/me/email/', ChangeEmailView.as_view(), name='change-email'),
    path(
        'users/me/email/confirm/',
        ConfirmEmailChangeView.as_view(),
        name='confirm-email-change',
    ),
    path('users/me/logout-all/', LogoutAllView.as_view(), name='logout-all'),
    path('users/me/delete/', DeleteAccountView.as_view(), name='delete-account'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path(
        'password-reset/confirm/',
        PasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
]
