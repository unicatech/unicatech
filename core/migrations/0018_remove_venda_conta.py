# Generated by Django 4.1.5 on 2023-04-13 21:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_venda_cliente"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="venda",
            name="conta",
        ),
    ]
