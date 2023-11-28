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
        #vendas = Venda.objects.filter(criados__month=mes_selecionado).filter(criados__year=ano_selecionado).filter(ativo=True).order_by('-id')
        vendas = Venda.objects.filter(criados__month='11').filter(criados__year='2023').order_by('-id')
        vendas_template = []
        venda_lucro = 0
        venda_lucro_total = 0
        venda_total = 0
        #Campo Resumo Lucro Líquido por Venda
        venda_identificador = 0
        venda_cliente_nome_cliente = ''
        venda_datavenda = ''
        primeira_vez = 1
        for venda in vendas:
            if primeira_vez:
               venda_identificador = venda.identificadorVenda
               primeira_vez = 0
            if (venda_identificador != venda.identificadorVenda):
                vendas_template.append(
                   {
                      'venda_id': venda_identificador,
                      #'nome_produtos': venda.produto_id.NomeProduto,
                      'cliente': venda_cliente_nome_cliente,
                      'precoProduto': venda.precoProduto,
                      'lucro': venda_lucro,
                      'data_venda': venda.criados
                    }
                )
                venda_lucro = 0
                logging.warning("Identificador Venda")
                logging.warning(venda_identificador)

            venda_lucro = venda_lucro + venda.lucro
            venda_cliente_nome_cliente = venda.cliente.nomeCliente
            venda_datavenda = venda.criados
            venda_preco_produto = venda.precoProduto
            venda_quantidade_produto = venda.quantidadeProduto
            venda_lucro_total = venda_lucro_total + venda.lucro
            venda_total = venda_total + venda_preco_produto * venda_quantidade_produto
            venda_identificador = venda.identificadorVenda
            #vendas_template.append(
            #{
            #    'venda_id': venda_identificador,
            #    # 'nome_produto': venda.produto_id.NomeProduto,
            #    'cliente': venda_cliente_nome_cliente,
            #    'precoProduto': venda.precoProduto,
            #    'lucro': venda_lucro,
            #    'data_venda': venda.criados
            #}
            #)
            venda_lucro_total = venda_lucro_total + venda_lucro
            venda_total = venda_total + venda_preco_produto * venda_quantidade_produto
        context['vendas'] = vendas_template
        context['lucro_total'] = venda_lucro_total
        context['vendas_total'] = venda_total
        return context