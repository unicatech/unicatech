# Generated by Django 4.1.5 on 2023-04-07 16:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_venda_cliente"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="venda",
            name="conta",
        ),
    ]
