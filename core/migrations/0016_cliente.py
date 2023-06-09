# Generated by Django 4.1.5 on 2023-04-13 21:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_remove_venda_cliente_venda_conta_delete_cliente"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criados", models.DateField(verbose_name="Criação")),
                ("modificado", models.DateField(auto_now_add=True, verbose_name="Atualização")),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo?")),
                ("nomeCliente", models.CharField(max_length=200, verbose_name="Descrição")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
