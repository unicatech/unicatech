from django.db import models
from django.contrib.auth.models import Group
from stdimage.models import StdImageField
from django.contrib.auth.models import User


# Create your models here.

class Base(models.Model):
    criados = models.DateTimeField('Criação', auto_now_add=True)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Alertas(Base):
    id = models.AutoField(primary_key=True)
    evento = models.CharField('Localização', max_length=200)
    novo = models.BooleanField('Ativo?', default=True)
    icone = models.CharField('Icone', max_length=200)
    identificador_compra = models.IntegerField(null=True, blank=True)
    identificador_venda = models.IntegerField(null=True, blank=True)
    identificador_servico = models.IntegerField(null=True, blank=True)

    usuarios_vistos = models.ManyToManyField(
        User, blank=True, related_name='alertas_vistos'
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas_criados'
    )

    def __str__(self):
        return str(self.id)
