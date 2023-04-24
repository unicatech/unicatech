# Generated by Django 4.1.5 on 2023-04-07 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='venda',
            name='cliente',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='core.cliente', verbose_name='Cliente'),
            preserve_default=False,
        ),
    ]
