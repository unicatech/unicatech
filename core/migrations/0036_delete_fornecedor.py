# Generated by Django 4.1.5 on 2023-05-15 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_remove_produto_categoria_delete_categoriaproduto_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Fornecedor',
        ),
    ]
