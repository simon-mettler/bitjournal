from django.contrib import admin

from .models import AnalyticsBoard
from .models import AnalyticsWidget

admin.site.register(AnalyticsBoard)
admin.site.register(AnalyticsWidget)
