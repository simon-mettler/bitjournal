from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0006_remove_signal_average_weighting'),
    ]

    operations = [
        migrations.AddField(
            model_name='signal',
            name='empty_days_as_zero',
            field=models.BooleanField(default=False),
        ),
    ]
