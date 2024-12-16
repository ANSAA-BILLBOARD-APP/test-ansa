# Generated by Django 5.0.4 on 2024-12-16 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_asset', '0013_billboards_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='billboards',
            name='payment_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='billboards',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('not_paid', 'Not_paid')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='dimensions',
            name='max_width',
            field=models.FloatField(help_text='Width of the media asset in square meters'),
        ),
    ]
