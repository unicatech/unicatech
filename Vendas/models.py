from django.db import models

# Create your models here.

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=False)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True
class Venda(Base):
    identificadorVenda = models.IntegerField()
    produto = models.ForeignKey('Produtos.Produto', verbose_name='Produto', on_delete=models.CASCADE)
    quantidadeProduto = models.FloatField(default=0)
    precoProduto = models.FloatField(default=0)
    descricao = models.CharField('Descrição', max_length=200)
    cliente = models.ForeignKey('Vendas.Cliente', verbose_name='Cliente', on_delete=models.CASCADE)
    lucro = models.FloatField(default=0)
    def __str__(self):
        return self.id

class Cliente(Base):
    nomeCliente = models.CharField('Descrição', max_length=200)
    def __str__(self):
        return self.id
