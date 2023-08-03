from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages


from Vendas.models import Venda

from datetime import date, datetime
import re
import logging
from django.utils import timezone
from Vendas.models import Venda
from Compras.models import Compra
from Produtos.models import Produto

class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        mes_selecionado = 0
        ano_selecionado = 0
        if self.request.GET.__contains__("mes_selecionado"):
            mes_selecionado = self.request.GET["mes_selecionado"]
            ano_selecionado = self.request.GET["ano_selecionado"]
        else:
            mes_selecionado = str(timezone.now().month)
            ano_selecionado = timezone.now().year
        logging.warning(mes_selecionado)
        logging.warning(ano_selecionado)
        #vendas = Venda.objects.filter(criados__month=mes_selecionado).filter(criados__year=ano_selecionado).filter(ativo=True)
        vendas = Venda.objects.filter(criados__month='6').filter(criados__year='2023').order_by('-id')
        vendas_template = []
        venda_total_produto = 0
        compra_total_produto = 0
        # Cálculo do preço médio de compra do produto vendido
        for venda in vendas:
            venda_total_produto = venda_total_produto + venda.quantidadeProduto * venda.precoProduto
            vendas_template.append(
                {
                    'produto_id': venda.produto_id,
                    #'nome_produto': venda.produto_id.NomeProduto,
                    'quantidadeProduto': venda.quantidadeProduto,
                    'precoProduto': venda.precoProduto,
                }
            )
        context['vendas'] = vendas_template
        return context