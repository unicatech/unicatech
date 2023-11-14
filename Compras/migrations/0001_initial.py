# Generated by Django 4.1.5 on 2023-05-09 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0033_delete_compra_delete_localizacaocompra'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalizacaoCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criados', models.DateField(verbose_name='Criação')),
                ('modificado', models.DateField(auto_now_add=True, verbose_name='Atualização')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('localizacaoCompra', models.CharField(max_length=200, verbose_name='Localização')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criados', models.DateField(verbose_name='Criação')),
                ('modificado', models.DateField(auto_now_add=True, verbose_name='Atualização')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('identificadorCompra', models.IntegerField()),
                ('quantidadeProduto', models.FloatField(default=0)),
                ('precoProduto', models.FloatField(default=0)),
                ('frete', models.FloatField(default=0)),
                ('descricao', models.CharField(max_length=200, verbose_name='Descrição')),
                ('conta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.conta', verbose_name='Produto')),
                ('fornecedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.fornecedor', verbose_name='Fornecedor')),
                ('idLocalizacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Compras.localizacaocompra', verbose_name='Localização')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.produto', verbose_name='Produto')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
