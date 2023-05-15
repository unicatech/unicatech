from django.db import models

from stdimage.models import StdImageField


# Create your models here.

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=False)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Cliente(Base):
    nomeCliente = models.CharField('Descrição', max_length=200)
    def __str__(self):
        return self.id

