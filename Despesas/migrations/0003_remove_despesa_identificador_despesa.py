# Generated by Django 4.1.5 on 2023-09-26 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Despesas', '0002_despesa_categoria'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='despesa',
            name='identificador_despesa',
        ),
    ]
