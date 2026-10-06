from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LogoutView, InstanceConfigView, HealthView,CookieTokenObtainPairView, CookieTokenRefreshView

router = DefaultRouter()

urlpatterns = [
    path('token/', CookieTokenObtainPairView.as_view()),
    path('token/refresh/', CookieTokenRefreshView.as_view()),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('config/', InstanceConfigView.as_view(), name='instance-config'),
    path('health/', HealthView.as_view(), name='health'),
    path('', include(router.urls)),
]
