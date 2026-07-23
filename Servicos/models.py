from django.db import models
from django.contrib.auth.models import User

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=False)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Servico(Base):
    identificador_servico = models.IntegerField()
    id_venda = models.IntegerField( null=True, default=0)
    descricao = models.CharField('Descrição', max_length=200)
    cliente = models.ForeignKey('Vendas.Cliente', verbose_name='Cliente', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    preco_servico = models.FloatField(default=0)
    imei = models.CharField('Descrição', max_length=200)
    def __str__(self):
        return self.id
