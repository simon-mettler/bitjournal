from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0005_tally_summary_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signal',
            name='average_weighting',
        ),
    ]
