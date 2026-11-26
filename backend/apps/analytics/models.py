"""
Analytics boards: named, ordered collections of widgets that display
information about signals.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from uuid import uuid7

from .choices import (
    WidgetCalculation,
    WidgetChartType,
    WidgetTimeframe,
    WidgetType,
)
from .widget_types import WIDGET_TYPES


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
    # Settings of the widget type, see widget_types.py.
    config = models.JSONField(default=dict, blank=True)
    timeframe = models.CharField(max_length=20, choices=WidgetTimeframe.choices)
    period_start = models.DateField(null=True, blank=True)
    days = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} in {self.board.name}"

    @property
    def definition(self):
        return WIDGET_TYPES[self.type]

    @property
    def settings(self) -> dict:
        return self.definition.with_defaults(self.config)

    def clean(self):
        if self.timeframe in (WidgetTimeframe.QUARTER, WidgetTimeframe.YEAR) and self.period_start is None:
            raise ValidationError('Quarter and year timeframes require period_start.')
        if self.timeframe == WidgetTimeframe.LAST_DAYS and not self.days:
            raise ValidationError('Last X days timeframe requires days to be at least 1.')
        if self.type not in WIDGET_TYPES:
            return  # reported by the choices validation of the field
        if self.timeframe in self.definition.excluded_timeframes:
            raise ValidationError(self.definition.excluded_timeframe_message)
        self.config = self.definition.clean_config(self.config)
