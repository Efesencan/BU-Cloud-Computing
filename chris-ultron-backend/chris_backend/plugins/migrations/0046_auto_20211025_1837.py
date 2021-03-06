# Generated by Django 2.2.24 on 2021-10-25 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0045_auto_20211020_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='computeresource',
            name='cpu_power',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AddField(
            model_name='computeresource',
            name='cpu_power_unit',
            field=models.CharField(blank=True, default='GHZ', max_length=300),
        ),
        migrations.AddField(
            model_name='computeresource',
            name='currency',
            field=models.CharField(blank=True, default='USD', max_length=300),
        ),
        migrations.AddField(
            model_name='computeresource',
            name='gpu_power',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AddField(
            model_name='computeresource',
            name='gpu_power_unit',
            field=models.CharField(blank=True, default='TFLOPS', max_length=300),
        ),
        migrations.AddField(
            model_name='computeresource',
            name='memory',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='computeresource',
            name='memory_unit',
            field=models.CharField(blank=True, default='GB', max_length=300),
        ),
    ]
