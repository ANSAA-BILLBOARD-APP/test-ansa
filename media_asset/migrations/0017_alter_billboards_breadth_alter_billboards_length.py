# Generated by Django 5.0.4 on 2025-02-13 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_asset', '0016_remove_billboards_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billboards',
            name='breadth',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='billboards',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
