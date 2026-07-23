"""
Logged events and their recorede values.
Depends on 'trackers'.

"""
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from uuid import uuid7

from apps.trackers.models import TrackerType

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
    )
    date = models.DateField()
    time = models.TimeField()
    note = models.TextField(blank=True)

    trackers = models.ManyToManyField(
        'trackers.Tracker',
        through='TrackerEntry',
        related_name='events',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['user', 'date'])
        ]

    def __str__(self):
        return f"Event {self.date} {self.time} ({self.user})"


class TrackerEntry(models.Model):
    """
    Actual recorded value for a tracker on a given event.
    Only one of 'value' or 'duration' should be populated, depending on the
    related tracker's type.

    """
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='entries')
    tracker = models.ForeignKey('trackers.tracker', on_delete=models.CASCADE, related_name='entries')

    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracker', 'event'])
        ]

    def clean(self):
        if self.tracker.type == TrackerType.DURATION:
            if self.duration is None:
                raise ValidationError('Duration trackers require duration to be set.')
            if self.value is not None:
                raise ValidationError('Duration trackers must not set value.')
        else:
            if self.value is None:
                raise ValidationError(f"{self.tracker.get_type_display()} tracker require value to be set.")
            if self.duration is not None:
                raise ValidationError('Only duration tracker may set duration.')

            if self.tracker.type == TrackerType.RANGE:
                cfg = self.tracker.range_config
                if not (cfg.min_value <= self.value <= cfg.maxvalue):
                    raise ValidationError(f"Value must be between {cfg.min_value} and {cfg.max_value}.")

    def __str__(self):
        return f"{self.tracker.name} @ {self.event}" 
