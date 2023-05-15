# Generated by Django 4.1.5 on 2023-05-09 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaProduto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criados', models.DateField(verbose_name='Criação')),
                ('modificado', models.DateField(auto_now_add=True, verbose_name='Atualização')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('categoria', models.CharField(max_length=20, verbose_name='Categoria')),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criados', models.DateField(verbose_name='Criação')),
                ('modificado', models.DateField(auto_now_add=True, verbose_name='Atualização')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('SKU', models.CharField(max_length=10, verbose_name='SKU')),
                ('NomeProduto', models.CharField(max_length=100, verbose_name='Nome do Produto')),
                ('estoque', models.IntegerField(default=0, verbose_name='Estoque')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Produtos.categoriaproduto', verbose_name='Categoria')),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
            },
        ),
    ]