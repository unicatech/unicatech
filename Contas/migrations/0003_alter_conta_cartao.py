# Generated by Django 4.1.5 on 2023-05-15 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Contas', '0002_alter_conta_categoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conta',
            name='cartao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Contas.cartao', verbose_name='Tipo'),
        ),
    ]
