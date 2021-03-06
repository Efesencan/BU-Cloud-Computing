# Generated by Django 2.1.4 on 2020-02-11 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plugininstances', '0010_auto_20200131_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pathparameter',
            name='value',
            field=models.CharField(max_length=16000),
        ),
        migrations.AlterField(
            model_name='plugininstancefile',
            name='fname',
            field=models.FileField(max_length=4000, upload_to=''),
        ),
        migrations.AlterField(
            model_name='strparameter',
            name='value',
            field=models.CharField(blank=True, max_length=600),
        ),
    ]
