from django.contrib import admin

from .models import Event
from .models import TrackerEntry

admin.site.register(Event)
admin.site.register(TrackerEntry)
