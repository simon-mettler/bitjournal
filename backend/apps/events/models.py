"""
Logged events and their recorede values.
Depends on 'signals'.

"""
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from uuid import uuid7

from apps.signals.models import SignalType

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

    signal = models.ManyToManyField(
        'signals.Signal',
        through='SignalEntry',
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


class SignalEntry(models.Model):
    """
    Actual recorded value for a signal on a given event.
    Only one of 'value' or 'duration' should be populated, depending on the
    related signals type.

    """
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='entries')
    signal = models.ForeignKey('signals.signal', on_delete=models.CASCADE, related_name='entries')

    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['signal', 'event'])
        ]

    def clean(self):
        if self.signal.type == SignalType.DURATION:
            if self.duration is None:
                raise ValidationError('Duration signals require duration to be set.')
            if self.value is not None:
                raise ValidationError('Duration signals must not set value.')
        else:
            if self.value is None:
                raise ValidationError(f"{self.signal.get_type_display()} signal require value to be set.")
            if self.duration is not None:
                raise ValidationError('Only duration signal may set duration.')

            if self.signal.type == SignalType.RANGE:
                cfg = self.signal.range_config
                if not (cfg.min_value <= self.value <= cfg.maxvalue):
                    raise ValidationError(f"Value must be between {cfg.min_value} and {cfg.max_value}.")

    def __str__(self):
        return f"{self.signal.name} @ {self.event}" 
