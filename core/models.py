from django.db import models

from stdimage.models import StdImageField

# Create your models here.

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=True)
    modificado = models.DateField('Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Produto(Base):
    SKU = models.CharField('SKU', max_length=10)
    NomeProduto = models.CharField('Nome do Produto', max_length=100)
    categoria = models.ForeignKey('core.CategoriaProduto', verbose_name='Categoria', on_delete=models.CASCADE)
    estoque = models.IntegerField('Estoque', default=0)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.SKU

class CategoriaProduto(Base):
    categoria = models.CharField('Categoria', max_length=20)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.categoria

class Conta(Base):
    nomeConta = models.CharField('Nome da Conta', max_length=100)
    categoria = models.ForeignKey('core.CategoriaConta', verbose_name='Tipo', on_delete=models.CASCADE)
    taxas = models.FloatField()
    saldoInicial = models.FloatField(blank=True, default=None)
    descricao = models.CharField('Descrição', max_length=200)
    taxacartao1 = models.FloatField(default=0)
    taxacartao2 = models.FloatField(default=0)
    taxacartao3 = models.FloatField(default=0)
    taxacartao4 = models.FloatField(default=0)
    taxacartao5 = models.FloatField(default=0)
    taxacartao6 = models.FloatField(default=0)
    taxacartao7 = models.FloatField(default=0)
    taxacartao8 = models.FloatField(default=0)
    taxacartao9 = models.FloatField(default=0)
    taxacartao10 = models.FloatField(default=0)
    taxacartao11 = models.FloatField(default=0)
    taxacartao12 = models.FloatField(default=0)
    taxacartao13 = models.FloatField(default=0)
    taxacartao14 = models.FloatField(default=0)
    taxacartao15 = models.FloatField(default=0)
    taxacartao16 = models.FloatField(default=0)
    taxacartao17 = models.FloatField(default=0)
    taxacartao18 = models.FloatField(default=0)

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
    contaCredito = models.IntegerField(default=0)
    contaDebito = models.IntegerField(default=0)
    valorCredito = models.FloatField(default=0)
    valorDebito = models.FloatField(default=0)
    identificadorCompra = models.IntegerField(default=0)
    identificadorVenda = models.IntegerField(default=0)
    descricao = models.CharField('Descrição', max_length=200)

    def __str__(self):
        return self.id

class Fornecedor(Base):
    nomeFornecedor = models.CharField('Descrição', max_length=200)

    def __str__(self):
        return self.id

class LocalizacaoCompra(Base):
    localizacaoCompra = models.CharField('Localização', max_length=200)

    def __str__(self):
        return self.id
class Compra(Base):
    identificadorCompra = models.IntegerField()
    fornecedor = models.ForeignKey('core.Fornecedor', verbose_name='Fornecedor', on_delete=models.CASCADE)
    produto = models.ForeignKey('core.Produto', verbose_name='Produto', on_delete=models.CASCADE)
    quantidadeProduto = models.FloatField(default=0)
    precoProduto = models.FloatField(default=0)
    frete = models.FloatField(default=0)
    descricao = models.CharField('Descrição', max_length=200)
    idLocalizacao = models.ForeignKey('core.LocalizacaoCompra', verbose_name='Localização', on_delete=models.CASCADE)


    def __str__(self):
        return self.id