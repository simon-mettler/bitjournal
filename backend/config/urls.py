from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.authentication.urls')),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.signals.urls')),
    path('api/', include('apps.boards.urls')),
    path('api/', include('apps.events.urls')),
    path('api/', include('apps.analytics.urls')),
]
