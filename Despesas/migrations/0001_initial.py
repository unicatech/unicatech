# Generated by Django 4.1.5 on 2023-09-26 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaDespesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criados', models.DateField(verbose_name='Criação')),
                ('modificado', models.DateField(auto_now_add=True, verbose_name='Atualização')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('categoria', models.CharField(max_length=200, verbose_name='Categoria')),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Despesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criados', models.DateField(verbose_name='Criação')),
                ('modificado', models.DateField(auto_now_add=True, verbose_name='Atualização')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('identificador_despesa', models.IntegerField()),
                ('nome_despesa', models.CharField(max_length=200, verbose_name='Descrição')),
                ('periodicidade', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
