from django.contrib import admin

from .models import TrackerBoard
from .models import BoardTracker

admin.site.register(TrackerBoard)
admin.site.register(BoardTracker)
