from django.db import models

from Contas.models import Conta
# Create your models here.

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=False)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class CadastroDespesa(Base):
    nome_despesa = models.CharField('Descrição', max_length=200)
    periodicidade = models.IntegerField()
    # categoria = models.ForeignKey('Despesas.CategoriaDespesa', verbose_name='Tipo', on_delete=models.CASCADE)
    conta_debito = models.ForeignKey('Contas.Conta', verbose_name='Tipo', on_delete=models.CASCADE)
    valor = models.FloatField()
    def __str__(self):
        return self.id

