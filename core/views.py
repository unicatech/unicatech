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
        venda_lucro_consolidado = 0
        #Campo Resumo Lucro Líquido por Venda
        listarVendasTemplate = []
        identificadorVenda = 0
        lucro_venda = 0
        valor_total_venda = 0
        valor_recebido_venda = 0
        quantidade_total_produtos = 0
        valor_excedente_venda_consolidado = 0
        total_a_receber_consolidado = 0
        valor_total_venda_consolidado = 0
        valor_recebido_venda_consolidado = 0
        for venda in vendas:
            quantidade_total_produtos = quantidade_total_produtos + venda.quantidadeProduto
            if identificadorVenda != venda.identificadorVenda:
                #Faturamento e lucro mensal
                vendaIdentificada = Venda.objects.filter(identificadorVenda=venda.identificadorVenda,ativo=True)
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
                #Valores totais a receber
                recebimentos_venda = MovimentacaoConta.objects.filter(identificadorVenda=venda.identificadorVenda,ativo=True)
                for recebimento_venda in recebimentos_venda:
                    valor_recebido_venda = valor_recebido_venda + recebimento_venda.valorCredito
                venda_lucro_consolidado = venda_lucro_consolidado + lucro_venda

                identificadorVenda = venda.identificadorVenda

                total_a_receber = valor_total_venda - valor_recebido_venda

                if total_a_receber < 0:
                    valor_excedente_venda_consolidado = valor_excedente_venda_consolidado - total_a_receber
                    total_a_receber = 0

                total_a_receber_consolidado = total_a_receber_consolidado + total_a_receber
                valor_total_venda_consolidado = valor_total_venda_consolidado + valor_total_venda
                valor_recebido_venda_consolidado = valor_recebido_venda_consolidado + valor_recebido_venda
                valor_total_venda = 0
                valor_recebido_venda = 0
                lucro_venda = 0

        #Cálculo do valor em estoque
        valor_total_estoque = 0
        produtos = Produto.objects.filter(estoque__gt = 0)
        for produto in produtos:
            compras_produto = Compra.objects.filter(produto_id=produto.id, ativo=True).order_by('-id')
            quantidade_produto_estoque = produto.estoque
            logging.warning("Produto " + produto.NomeProduto)
            for compra in compras_produto:
                if compra.quantidadeProduto >= quantidade_produto_estoque:
                    logging.warning( str(compra.quantidadeProduto) + " " +
                        str(produto.estoque) + " " + str(compra.valorDolarMedio) + " " + str(compra.precoProduto))
                    valor_total_estoque = (valor_total_estoque +
                                            float(compra.precoProduto) * compra.valorDolarMedio * quantidade_produto_estoque)
                    break
                else:
                    valor_total_estoque = (valor_total_estoque +
                                            float(compra.precoProduto) * compra.valorDolarMedio * compra.quantidadeProduto)
                    quantidade_produto_estoque = quantidade_produto_estoque - compra.quantidadeProduto

        context['vendas'] = listarVendasTemplate
        context['venda_lucro_total'] = venda_lucro_consolidado

        context['valor_total_venda'] = valor_total_venda_consolidado
        context['valor_recebido_venda'] = valor_recebido_venda_consolidado
        context['total_a_receber'] = total_a_receber_consolidado
        context['valor_excedente_venda'] = valor_excedente_venda_consolidado
        if quantidade_total_produtos > 0:
            context['ticket_medio'] = valor_total_venda_consolidado / quantidade_total_produtos
        else:
            context['ticket_medio'] = 0
        context['valor_total_estoque'] = valor_total_estoque
        return context