# Create your models here.
from django.db import models

class Dummy(models.Model):
    class Meta:
        managed = False              # não cria tabela no banco
        verbose_name = "Relatorio"
        verbose_name_plural = "Relatorios"