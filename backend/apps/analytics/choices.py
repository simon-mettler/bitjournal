"""Choices shared by the models and the widget type definitions."""

from django.db import models


class WidgetType(models.TextChoices):
    VALUE = 'value', 'Display value'
    TIMESERIES = 'timeseries', 'Over time'


class WidgetAggregation(models.TextChoices):
    TOTAL = 'total', 'Total'
    AVERAGE = 'average', 'Average'
    PER_EVENT = 'per_event', 'Average per event'


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


class WidgetChartType(models.TextChoices):
    BAR = 'bar', 'Bar'
    LINE = 'line', 'Line'
