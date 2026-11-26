"""
One definition per widget type: the settings stored in AnalyticsWidget.config,
the rules that apply to them and the data the widget shows.

A new type needs a WidgetType choice and a definition in WIDGET_TYPES.
"""

from dataclasses import dataclass

from django.core.exceptions import ValidationError

from .calculations import available_calculations
from .choices import WidgetCalculation, WidgetChartType, WidgetTimeframe, WidgetType


@dataclass(frozen=True)
class Setting:
    """One key of a widget's config. Without choices it is a boolean."""

    default: str | bool
    choices: tuple[str, ...] | None = None

    def is_valid(self, value) -> bool:
        if self.choices is None:
            return isinstance(value, bool)
        return isinstance(value, str) and value in self.choices


class WidgetDefinition:
    settings: dict[str, Setting] = {}
    excluded_timeframes: tuple[str, ...] = ()
    excluded_timeframe_message = ''

    def with_defaults(self, config: dict) -> dict:
        return {**{key: setting.default for key, setting in self.settings.items()}, **config}

    def clean_config(self, config) -> dict:
        """
        Checks the shape of a config and fills in defaults. Does not look at the signal:
        signals can be edited later, so stored widgets (and imports) must stay valid.
        """
        if not isinstance(config, dict):
            raise ValidationError('Widget config must be an object.')
        if unknown := sorted(set(config) - set(self.settings)):
            raise ValidationError(f'Unknown widget settings: {", ".join(unknown)}.')
        for key, value in config.items():
            if not self.settings[key].is_valid(value):
                raise ValidationError(f'Invalid value for widget setting "{key}".')
        return self.with_defaults(config)

    def config_for_signal(self, config: dict, signal) -> dict:
        if 'calculation' in config and config['calculation'] not in available_calculations(signal):
            raise ValidationError('This calculation is not available for the signal.')
        return config

    def data(self, widget_data) -> dict:
        """The type specific part of a widget's values, see services.WidgetData."""
        raise NotImplementedError


CALCULATION = Setting(WidgetCalculation.TOTAL.value, tuple(WidgetCalculation.values))


class ValueDefinition(WidgetDefinition):
    settings = {'calculation': CALCULATION}

    def data(self, widget_data):
        totals = widget_data.totals
        calculation = widget_data.calculation
        has_value = (
            totals['count']
            or calculation == WidgetCalculation.TOTAL
            or (calculation == WidgetCalculation.DAILY_AVERAGE
                and widget_data.signal.empty_days_as_zero)
        )
        return {'value': totals[calculation] if has_value else None, 'timeseries': None}


class TimeseriesDefinition(WidgetDefinition):
    settings = {
        'calculation': CALCULATION,
        'chart_type': Setting(WidgetChartType.BAR.value, tuple(WidgetChartType.values)),
        'show_average': Setting(True),
    }
    excluded_timeframes = (WidgetTimeframe.TODAY, WidgetTimeframe.YESTERDAY)
    excluded_timeframe_message = 'Over time widgets need a timeframe of more than one day.'

    def data(self, widget_data):
        return {'value': None, 'timeseries': widget_data.timeseries()}


WIDGET_TYPES: dict[str, WidgetDefinition] = {
    WidgetType.VALUE: ValueDefinition(),
    WidgetType.TIMESERIES: TimeseriesDefinition(),
}
