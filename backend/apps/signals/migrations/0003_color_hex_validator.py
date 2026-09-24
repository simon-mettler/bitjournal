import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signal',
            name='color',
            field=models.CharField(blank=True, max_length=7, validators=[django.core.validators.RegexValidator(message='Color must be a hex value in the format #rrggbb.', regex='^#[0-9a-fA-F]{6}$')]),
        ),
        migrations.AlterField(
            model_name='signalcategory',
            name='color',
            field=models.CharField(blank=True, max_length=7, validators=[django.core.validators.RegexValidator(message='Color must be a hex value in the format #rrggbb.', regex='^#[0-9a-fA-F]{6}$')]),
        ),
    ]
