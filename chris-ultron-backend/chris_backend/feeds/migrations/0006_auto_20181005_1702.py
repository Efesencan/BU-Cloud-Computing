# Generated by Django 2.0.7 on 2018-10-05 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0005_auto_20170301_1312'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-creation_date',)},
        ),
        migrations.AlterModelOptions(
            name='feedfile',
            options={'ordering': ('fname',)},
        ),
        migrations.AlterModelOptions(
            name='note',
            options={},
        ),
        migrations.AlterField(
            model_name='feedfile',
            name='plugin_inst',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='plugins.PluginInstance'),
        ),
    ]
