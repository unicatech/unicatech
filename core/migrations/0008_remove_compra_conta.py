# Generated by Django 4.1.5 on 2023-04-02 14:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_compra_conta"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="compra",
            name="conta",
        ),
    ]
