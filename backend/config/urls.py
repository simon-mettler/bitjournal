from django.contrib import admin
from django.urls import path, re_path, include

from .views import spa_index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.authentication.urls')),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.signals.urls')),
    path('api/', include('apps.boards.urls')),
    path('api/', include('apps.events.urls')),
    path('api/', include('apps.analytics.urls')),
    # SPA fallback: anything that isn't api/admin/static or a missing file (has an extension).
    re_path(r'^(?!(?:api|admin|static)(?:/|$))(?P<path>(?:.*/)?[^/.]*)$', spa_index),
]
