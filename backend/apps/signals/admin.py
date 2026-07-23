from django.contrib import admin

from .models import Signal 
from .models import SignalCategory
from .models import SignalValueConfig
from .models import SignalRangeConfig

admin.site.register(Signal)
admin.site.register(SignalCategory)
admin.site.register(SignalValueConfig)
admin.site.register(SignalRangeConfig)
