from django.contrib import admin
from .models import Event, SignalEntry

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "occurred_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(SignalEntry)
class SignalEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event",
        "signal",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
