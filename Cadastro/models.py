
# Create your models here.
from django.db import models

class Dummy(models.Model):
    class Meta:
        managed = False              # não cria tabela no banco
        verbose_name = "Cadastro"
        verbose_name_plural = "Cadastros"