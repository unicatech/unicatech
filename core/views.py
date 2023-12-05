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
from Contas.models import MovimentacaoConta

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
        vendas = Venda.objects.filter(criados__month=mes_selecionado).filter(criados__year=ano_selecionado).filter(ativo=True).order_by('-id')
        #vendas = Venda.objects.filter(criados__month='11').filter(criados__year='2023').filter(ativo=True).order_by('-id')
        vendas_template = []
        venda_lucro = 0
        venda_lucro_total = 0
        venda_total = 0
        #Campo Resumo Lucro Líquido por Venda
        listarVendasTemplate = []
        recebimentos = []
        identificadorVenda = 0
        lucro_venda = 0
        valor_total_venda = 0
        valor_recebido_venda = 0
        total_a_receber = 0
        for venda in vendas:
            if identificadorVenda != venda.identificadorVenda:
                #Faturamento e lucro mensal
                vendaIdentificada = Venda.objects.filter(identificadorVenda=venda.identificadorVenda,ativo=True).order_by('identificadorVenda')
                for venda in vendaIdentificada:
                    lucro_venda = lucro_venda + venda.lucro
                    valor_total_venda = valor_total_venda + venda.quantidadeProduto * venda.precoProduto
                listarVendasTemplate.append(
                    {
                     'venda_id': venda.identificadorVenda,
                     'nome_cliente': venda.cliente.nomeCliente,
                     'data_venda': venda.criados,
                     'lucro_venda': lucro_venda,
                     }
                )
                venda_lucro_total = venda_lucro_total + lucro_venda
                lucro_venda = 0
                identificadorVenda = venda.identificadorVenda

                #Valor recebido e valor devido no período
                recebimentos_venda = MovimentacaoConta.objects.filter(identificadorVenda=venda.identificadorVenda,
                                                                      ativo=True)
                for recebimento_venda in recebimentos_venda:
                    if recebimento_venda.valorCredito <= 0:
                        continue
                    else:
                        valor_recebido_venda = valor_recebido_venda + recebimento_venda.valorCredito
        total_a_receber = valor_total_venda - valor_recebido_venda
        context['vendas'] = listarVendasTemplate
        context['venda_lucro_total'] = venda_lucro_total
        context['valor_total_venda'] = valor_total_venda
        context['valor_recebido_venda'] = valor_recebido_venda
        context['total_a_receber'] = total_a_receber
        return context