from django.db import models

# Create your models here.
class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=False)
    modificado = models.DateField('Atualização', auto_now_add=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Produto(Base):
    SKU = models.CharField('SKU', max_length=10)
    NomeProduto = models.CharField('Nome do Produto', max_length=100)
    categoria = models.ForeignKey('Produtos.CategoriaProduto', verbose_name='Categoria', on_delete=models.CASCADE)
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
