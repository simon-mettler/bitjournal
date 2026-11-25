from django.db import migrations


def sum_tallies(apps, schema_editor):
    Signal = apps.get_model('signals', 'Signal')
    Signal.objects.filter(type='tally', summary_method='average').update(summary_method='total')


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0004_signal_average_weighting'),
    ]

    operations = [
        migrations.RunPython(sum_tallies, migrations.RunPython.noop),
    ]
