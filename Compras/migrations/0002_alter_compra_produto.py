# Generated by Django 4.1.5 on 2023-05-15 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Produtos', '0001_initial'),
        ('Compras', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compra',
            name='produto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Produtos.produto', verbose_name='Produto'),
        ),
    ]