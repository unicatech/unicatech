# Generated by Django 4.1.5 on 2023-03-06 13:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_remove_compra_datacompra"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movimentacaoconta",
            name="identificadorCompra",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="movimentacaoconta",
            name="identificadorvenda",
            field=models.IntegerField(default=0),
        ),
    ]
