# Generated by Django 4.1.5 on 2023-04-27 23:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_alter_venda_cliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimentacaoconta',
            name='contaCredito',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.conta', verbose_name='Conta'),
        ),
    ]