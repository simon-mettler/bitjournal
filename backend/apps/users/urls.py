from django.urls import path
from .views import MeView, ChangePasswordView, DeleteAccountView, LogoutAllView

urlpatterns = [
    path('users/me/', MeView.as_view()),
    path('users/me/password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/me/logout-all/', LogoutAllView.as_view(), name='logout-all'),
    path('users/me/delete/', DeleteAccountView.as_view(), name='delete-account'),
]
