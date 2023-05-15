# Generated by Django 4.1.5 on 2023-05-15 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Compras', '0002_alter_compra_produto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fornecedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criados', models.DateField(verbose_name='Criação')),
                ('modificado', models.DateField(auto_now_add=True, verbose_name='Atualização')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('nomeFornecedor', models.CharField(max_length=200, verbose_name='Descrição')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='compra',
            name='fornecedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Compras.fornecedor', verbose_name='Fornecedor'),
        ),
    ]
