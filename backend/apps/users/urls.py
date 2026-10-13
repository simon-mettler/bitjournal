from django.urls import path
from .views import MeView, LogoutAllView

urlpatterns = [
    path('users/me/', MeView.as_view()),
    path('users/me/logout-all/', LogoutAllView.as_view(), name='logout-all'),
]
