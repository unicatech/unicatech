# Generated by Django 4.1.5 on 2023-04-02 14:49

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_remove_compra_conta"),
    ]

    operations = [
        migrations.AddField(
            model_name="compra",
            name="conta",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="core.conta", verbose_name="Produto"
            ),
            preserve_default=False,
        ),
    ]
