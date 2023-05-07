# Generated by Django 4.1.5 on 2023-04-07 16:21

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_alter_categoriaconta_criados_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Venda",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criados", models.DateField(verbose_name="Criação")),
                ("modificado", models.DateField(auto_now_add=True, verbose_name="Atualização")),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo?")),
                ("identificadorVenda", models.IntegerField()),
                ("quantidadeProduto", models.FloatField(default=0)),
                ("precoProduto", models.FloatField(default=0)),
                ("descricao", models.CharField(max_length=200, verbose_name="Descrição")),
                (
                    "conta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.conta", verbose_name="Produto"
                    ),
                ),
                (
                    "produto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.produto", verbose_name="Produto"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
