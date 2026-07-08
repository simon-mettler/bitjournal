from django.contrib import admin

from .models import Tracker
from .models import TrackerCategory
from .models import TrackerValueConfig
from .models import TrackerRangeConfig

admin.site.register(Tracker)
admin.site.register(TrackerCategory)
admin.site.register(TrackerValueConfig)
admin.site.register(TrackerRangeConfig)
