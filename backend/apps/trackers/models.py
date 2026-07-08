"""
Core models that define what can be tracked, including 
tracker definitions, categories and type specific configuration.
Does not depend on any other app.

"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class TrackerType(models.TextChoices):
    TALLY = 'tally', 'Tally'
    RANGE = 'range', 'Range'
    VALUE = 'value', 'Value'
    DURATION = 'duration', 'Duration'


class SummaryMethod(models.TextChoices):
    AVERAGE = 'average', 'Average'
    SUM = 'sum', 'Sum (total)'


class TrackerCategory(models.Model):
    """ User defined grouping for trackers."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tracker_categories',
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_category_name_per_user')
        ]
        ordering = ['name']
        verbose_name_plural = 'tracker categories'

    def __str__(self):
        return self.name


class Tracker(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trackers',
    )
    category = models.ForeignKey(
        TrackerCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trackers'
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TrackerType.choices)
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
            original_type = Tracker.objects.filter(pk=self.pk).values_list('type', flat=True).first()
            if original_type is not None and original_type != self.type:
                raise ValidationError('Tracker type cannot be changed after creation.')

        if self.type == TrackerType.RANGE and not hasattr(self, 'range_config'):
            raise ValidationError("Range trackers require a range_config.")
        if self.type == TrackerType.VALUE and not hasattr(self, 'value_config'):
            raise ValidationError('Value tracker require a value_config.')


class TrackerRangeConfig(models.Model):
    """Additional attributes for TrackerType.RANGE."""

    tracker = models.OneToOneField(
        Tracker,
        on_delete=models.CASCADE,
        related_name='range_config',
        limit_choices_to={'type': TrackerType.RANGE},
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


class TrackerValueConfig(models.Model):
    """Additional attributes for TrackerType.VALUE."""

    tracker = models.OneToOneField(
        Tracker,
        on_delete=models.CASCADE,
        related_name='value_config',
        limit_choices_to={'type': TrackerType.VALUE},
    )
    unit = models.CharField(max_length=20)
