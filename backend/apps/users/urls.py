from django.urls import path
from .views import (
    ChangePasswordView,
    DeleteAccountView,
    LogoutAllView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
)

urlpatterns = [
    path('users/me/', MeView.as_view()),
    path('users/me/password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/me/logout-all/', LogoutAllView.as_view(), name='logout-all'),
    path('users/me/delete/', DeleteAccountView.as_view(), name='delete-account'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path(
        'password-reset/confirm/',
        PasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
]
