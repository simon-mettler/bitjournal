"""
One definition per widget type: the settings stored in AnalyticsWidget.config,
the rules that apply to them and the data the widget shows.

A new type needs a WidgetType choice and a definition in WIDGET_TYPES.
"""

from dataclasses import dataclass

from django.core.exceptions import ValidationError

from apps.signals.models import SignalType, SummaryMethod

from .choices import WidgetAggregation, WidgetChartType, WidgetTimeframe, WidgetType


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
        """Applied when a user saves a widget: reject or adjust settings that don't fit the signal."""
        return config

    def data(self, widget_data) -> dict:
        """The type specific part of a widget's values, see services.WidgetData."""
        raise NotImplementedError


class ValueDefinition(WidgetDefinition):
    settings = {
        'aggregation': Setting(WidgetAggregation.TOTAL.value, tuple(WidgetAggregation.values)),
    }

    def config_for_signal(self, config, signal):
        if config['aggregation'] != WidgetAggregation.PER_EVENT:
            return config
        if signal.type == SignalType.TALLY:
            raise ValidationError('Every tally event counts as 1, so there is no average per event.')
        # the average of an average signal already follows its own weighting
        if signal.summary_method == SummaryMethod.AVERAGE:
            return {**config, 'aggregation': WidgetAggregation.AVERAGE.value}
        return config

    def data(self, widget_data):
        totals = widget_data.totals
        aggregation = widget_data.config['aggregation']
        if aggregation == WidgetAggregation.TOTAL:
            value = totals['total']
        elif not totals['count']:
            value = None
        elif (aggregation == WidgetAggregation.PER_EVENT
              and widget_data.signal.summary_method == SummaryMethod.SUM):
            value = totals['total'] / totals['count']  # today included, an event is never unfinished
        else:
            value = totals['average']
        return {'value': value, 'timeseries': None}


class TimeseriesDefinition(WidgetDefinition):
    settings = {
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
