# Generated by Django 4.1.5 on 2023-09-26 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Despesas', '0003_remove_despesa_identificador_despesa'),
    ]

    operations = [
        migrations.AddField(
            model_name='despesa',
            name='valor',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
