# Generated by Django 4.1.5 on 2023-04-13 23:37

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_remove_venda_conta"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venda",
            name="cliente",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="core.cliente", verbose_name="Cliente"
            ),
        ),
    ]
