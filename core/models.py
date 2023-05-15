from django.db import models

from stdimage.models import StdImageField


# Create your models here.

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=False)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True




class Conta(Base):
    nomeConta = models.CharField('Nome da Conta', max_length=100)
    categoria = models.ForeignKey('core.CategoriaConta', verbose_name='Tipo', on_delete=models.CASCADE)
    taxas = models.FloatField()
    saldoInicial = models.FloatField(blank=True, default=None)
    descricao = models.CharField('Descrição', max_length=200)
    cartao = models.ForeignKey('core.Cartao', verbose_name='Tipo', on_delete=models.CASCADE, null=True)
    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'

    def __str__(self):
        return self.nomeConta

class Cartao(Base):
    cartao = models.IntegerField(null=True)
    bandeira_cartao = models.CharField('Bandeira do Cartão', max_length=20)
    taxa_cartao1 = models.FloatField(default=0)
    taxa_cartao2 = models.FloatField(default=0)
    taxa_cartao3 = models.FloatField(default=0)
    taxa_cartao4 = models.FloatField(default=0)
    taxa_cartao5 = models.FloatField(default=0)
    taxa_cartao6 = models.FloatField(default=0)
    taxa_cartao7 = models.FloatField(default=0)
    taxa_cartao8 = models.FloatField(default=0)
    taxa_cartao9 = models.FloatField(default=0)
    taxa_cartao10 = models.FloatField(default=0)
    taxa_cartao11 = models.FloatField(default=0)
    taxa_cartao12 = models.FloatField(default=0)
    taxa_cartao13 = models.FloatField(default=0)
    taxa_cartao14 = models.FloatField(default=0)
    taxa_cartao15 = models.FloatField(default=0)
    taxa_cartao16 = models.FloatField(default=0)
    taxa_cartao17 = models.FloatField(default=0)
    taxa_cartao18 = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'

    def __str__(self):
        return self.nomeConta


class CategoriaConta(Base):
    categoria = models.CharField('Categoria', max_length=200)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.categoria


class MovimentacaoConta(Base):
    contaCredito = models.ForeignKey('core.Conta', verbose_name='Conta', on_delete=models.CASCADE, null=True)
    contaDebito = models.IntegerField(default=0)
    valorCredito = models.FloatField(default=0)
    valorDebito = models.FloatField(default=0)
    identificadorCompra = models.IntegerField(default=0)
    identificadorVenda = models.IntegerField(default=0)
    descricao = models.CharField('Descrição', max_length=200)

    def __str__(self):
        return self.id


class Cliente(Base):
    nomeCliente = models.CharField('Descrição', max_length=200)
    def __str__(self):
        return self.id

