"""
Analytics boards: named, ordered collections of widgets that display
information about signals.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from uuid import uuid7


class WidgetType(models.TextChoices):
    VALUE = 'value', 'Display value'


class WidgetAggregation(models.TextChoices):
    TOTAL = 'total', 'Total'
    AVERAGE = 'average', 'Average'


class WidgetTimeframe(models.TextChoices):
    TODAY = 'today', 'Today'
    YESTERDAY = 'yesterday', 'Yesterday'
    THIS_WEEK = 'this_week', 'This week'
    LAST_WEEK = 'last_week', 'Last week'
    THIS_MONTH = 'this_month', 'This month'
    LAST_MONTH = 'last_month', 'Last month'
    THIS_QUARTER = 'this_quarter', 'This quarter'
    QUARTER = 'quarter', 'Quarter'
    THIS_YEAR = 'this_year', 'This year'
    YEAR = 'year', 'Year'
    LAST_DAYS = 'last_days', 'Last X days'


class AnalyticsBoard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics_boards',
    )
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_analytics_board_name_per_user'),
        ]

    def __str__(self):
        return self.name


class AnalyticsWidget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    board = models.ForeignKey(AnalyticsBoard, on_delete=models.CASCADE, related_name='widgets')
    order = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=20, choices=WidgetType.choices, default=WidgetType.VALUE)
    title = models.CharField(max_length=100)

    signal = models.ForeignKey('signals.Signal', on_delete=models.CASCADE, related_name='analytics_widgets')
    aggregation = models.CharField(
        max_length=10,
        choices=WidgetAggregation.choices,
        default=WidgetAggregation.TOTAL,
    )
    timeframe = models.CharField(max_length=20, choices=WidgetTimeframe.choices)
    period_start = models.DateField(null=True, blank=True)
    days = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} in {self.board.name}"

    def clean(self):
        if self.timeframe in (WidgetTimeframe.QUARTER, WidgetTimeframe.YEAR) and self.period_start is None:
            raise ValidationError('Quarter and year timeframes require period_start.')
        if self.timeframe == WidgetTimeframe.LAST_DAYS and not self.days:
            raise ValidationError('Last X days timeframe requires days to be at least 1.')
