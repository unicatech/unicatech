from django.db import models
from django.contrib.auth.models import Group
from stdimage.models import StdImageField


# Create your models here.

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=False)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Alertas(Base):
    id = models.AutoField(primary_key=True)
    evento = models.CharField('Localização', max_length=200)
    def __str__(self):
        return self.id