# Generated by Django 4.1.5 on 2023-05-04 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_remove_conta_taxacartao1_remove_conta_taxacartao10_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartao',
            name='bandeira_cartao',
            field=models.CharField(default=1, max_length=20, verbose_name='Bandeira do Cartão'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cartao',
            name='cartao',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
