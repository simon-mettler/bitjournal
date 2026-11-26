"""
Replaces the value widget's 'aggregation' and the signal's average weighting with one explicit
'calculation' per widget, so that widgets keep showing the same numbers.

Reads average_weighting, so it has to run before signals removes that field (see run_before,
which keeps signals independent of analytics).
"""

from django.db import migrations


def calculation_of(signal, aggregation):
    """The calculation matching what a widget showed. aggregation is None for timeseries."""
    if aggregation == 'total':
        return 'total'
    if signal.summary_method == 'total':
        if aggregation is None:
            return 'total'
        result = 'average' if aggregation == 'per_event' else 'daily_average'
    else:
        result = 'daily_average' if signal.average_weighting == 'day' else 'average'
    # every tally entry counts as 1, so there is no average per entry
    return 'daily_average' if signal.type == 'tally' and result == 'average' else result


def _update(apps, schema_editor, convert):
    widgets_of = apps.get_model('analytics', 'AnalyticsWidget').objects.using(
        schema_editor.connection.alias)
    widgets = list(widgets_of.select_related('signal'))
    for widget in widgets:
        widget.config = convert(widget)
    widgets_of.bulk_update(widgets, ['config'], batch_size=500)


def to_calculation(apps, schema_editor):
    def convert(widget):
        config = dict(widget.config)
        is_value = widget.type == 'value'
        aggregation = config.pop('aggregation', 'total') if is_value else None
        return {**config, 'calculation': calculation_of(widget.signal, aggregation)}

    _update(apps, schema_editor, convert)


def to_aggregation(apps, schema_editor):
    """
    Approximate: the old settings can't express every calculation, and average weighting
    comes back with its default.
    """
    def convert(widget):
        config = dict(widget.config)
        calculation = config.pop('calculation', 'total')
        if widget.type != 'value':
            return config
        if calculation == 'average' and widget.signal.summary_method == 'total':
            return {**config, 'aggregation': 'per_event'}
        return {**config, 'aggregation': 'total' if calculation == 'total' else 'average'}

    _update(apps, schema_editor, convert)


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0004_widget_config'),
        ('signals', '0005_tally_summary_total'),
    ]

    run_before = [('signals', '0006_remove_signal_average_weighting')]

    operations = [
        migrations.RunPython(to_calculation, to_aggregation),
    ]
