# Generated by Django 4.1.5 on 2023-05-09 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_delete_venda'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Compra',
        ),
        migrations.DeleteModel(
            name='LocalizacaoCompra',
        ),
    ]
