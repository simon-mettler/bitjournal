from django.db import migrations, models

# The config keys of each widget type at the time of this migration; they were columns before.
CONFIG_KEYS = {
    'value': ('aggregation',),
    'timeseries': ('chart_type', 'show_average'),
}


def columns_to_config(apps, schema_editor):
    AnalyticsWidget = apps.get_model('analytics', 'AnalyticsWidget')
    widgets = list(AnalyticsWidget.objects.using(schema_editor.connection.alias).all())
    for widget in widgets:
        widget.config = {key: getattr(widget, key) for key in CONFIG_KEYS[widget.type]}
    AnalyticsWidget.objects.using(schema_editor.connection.alias).bulk_update(
        widgets, ['config'], batch_size=500)


def config_to_columns(apps, schema_editor):
    """Settings a type doesn't have keep the column default."""
    AnalyticsWidget = apps.get_model('analytics', 'AnalyticsWidget')
    widgets = list(AnalyticsWidget.objects.using(schema_editor.connection.alias).all())
    for widget in widgets:
        for key in CONFIG_KEYS[widget.type]:
            if key in widget.config:
                setattr(widget, key, widget.config[key])
    AnalyticsWidget.objects.using(schema_editor.connection.alias).bulk_update(
        widgets, ['aggregation', 'chart_type', 'show_average'], batch_size=500)


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_alter_analyticswidget_aggregation'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyticswidget',
            name='config',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.RunPython(columns_to_config, config_to_columns),
        migrations.RemoveField(model_name='analyticswidget', name='aggregation'),
        migrations.RemoveField(model_name='analyticswidget', name='chart_type'),
        migrations.RemoveField(model_name='analyticswidget', name='show_average'),
    ]
