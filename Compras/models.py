from django.db import models

# Create your models here.

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=False)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Compra(Base):
    identificadorCompra = models.IntegerField()
    fornecedor = models.ForeignKey('Compras.Fornecedor', verbose_name='Fornecedor', on_delete=models.CASCADE)
    produto = models.ForeignKey('Produtos.Produto', verbose_name='Produto', on_delete=models.CASCADE)
    conta = models.ForeignKey('Contas.Conta', verbose_name='Produto', on_delete=models.CASCADE)
    quantidadeProduto = models.IntegerField(default=0)
    precoProduto = models.FloatField(default=0)
    frete = models.FloatField(default=0)
    descricao = models.CharField('Descrição', max_length=200)
    idLocalizacao = models.ForeignKey('Compras.LocalizacaoCompra', verbose_name='Localização', on_delete=models.CASCADE)
    valorDolarMedio = models.FloatField(default=0)
    def __str__(self):
        return self.id

    @property
    def valor_compra(self):
        return self.quantidadeProduto * self.precoProduto


class LocalizacaoCompra(Base):
    localizacaoCompra = models.CharField('Localização', max_length=200)
    def __str__(self):
        return self.id

class Deslocamento(Base):
    origem = models.IntegerField()
    destino = models.IntegerField()
    frete = models.FloatField(default=0)
    identificadorCompra = models.IntegerField()
    def __str__(self):
        return self.id
class Fornecedor(Base):
    nomeFornecedor = models.CharField('Descrição', max_length=200)
    localizacaoCompra = models.ForeignKey('Compras.LocalizacaoCompra', verbose_name='Localização da Compra', on_delete=models.CASCADE)
    def __str__(self):
        return self.id

