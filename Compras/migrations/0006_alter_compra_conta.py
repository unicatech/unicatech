# Generated by Django 4.1.5 on 2023-05-15 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Compras', '0005_remove_compra_remover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compra',
            name='conta',
            field=models.IntegerField(),
        ),
    ]
