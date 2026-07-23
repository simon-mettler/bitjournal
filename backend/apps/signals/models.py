"""
Core models that defines signals, including 
signal definitions, categories and type specific configuration.
Does not depend on any other app.

"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from uuid import uuid7

class SignalType(models.TextChoices):
    TALLY = 'tally', 'Tally'
    RANGE = 'range', 'Range'
    VALUE = 'value', 'Value'
    DURATION = 'duration', 'Duration'


class SummaryMethod(models.TextChoices):
    AVERAGE = 'average', 'Average'
    SUM = 'total', 'Total'


class SignalCategory(models.Model):
    """ User defined grouping for signals."""

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='signal_categories',
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_category_name_per_user')
        ]
        ordering = ['name']
        verbose_name_plural = 'signal categories'

    def __str__(self):
        return self.name


class Signal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='signals',
    )
    category = models.ForeignKey(
        SignalCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signals'
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=SignalType.choices)
    icon= models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True)
    summary_method = models.CharField(
        max_length=10,
        choices=SummaryMethod.choices,
        default=SummaryMethod.SUM
    )

    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def clean(self):
        if self.pk is not None:
            original_type = Signal.objects.filter(pk=self.pk).values_list('type', flat=True).first()
            if original_type is not None and original_type != self.type:
                raise ValidationError('Signal type cannot be changed after creation.')

        if self.type == SignalType.RANGE and not hasattr(self, 'range_config'):
            raise ValidationError("Range signals require a range_config.")
        if self.type == SignalType.VALUE and not hasattr(self, 'value_config'):
            raise ValidationError('Value signal require a value_config.')


class SignalRangeConfig(models.Model):
    """Additional attributes for SignalType.RANGE."""

    signal = models.OneToOneField(
        Signal,
        on_delete=models.CASCADE,
        related_name='range_config',
        limit_choices_to={'type': SignalType.RANGE},
    )
    min_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_label = models.CharField(max_length=50, blank=True)
    max_label = models.CharField(max_length=50, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(max_value__gt=models.F('min_value')),
                name='range_max_gt_min'
            )
        ]

    def clean(self):
        if self.max_value <= self.min_value:
            raise ValidationError('max_value mus be greater than min_value.')


class SignalValueConfig(models.Model):
    """Additional attributes for SignalType.VALUE."""

    signal = models.OneToOneField(
        Signal,
        on_delete=models.CASCADE,
        related_name='value_config',
        limit_choices_to={'type': SignalType.VALUE},
    )
    unit = models.CharField(max_length=20)
