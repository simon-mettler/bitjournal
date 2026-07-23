from django.contrib import admin

from .models import SignalBoard
from .models import BoardSignal

admin.site.register(SignalBoard)
admin.site.register(BoardSignal)
