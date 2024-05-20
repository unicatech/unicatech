from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from decimal import Decimal


from Vendas.models import Venda

from datetime import date, datetime
import re
import logging
from django.utils import timezone
from Vendas.models import Venda
from Compras.models import Compra, Deslocamento
from Produtos.models import Produto
from Contas.models import MovimentacaoConta, Conta
from Despesas.models import CadastroDespesa, Despesa
from Contas.views import MovimentacaoFinanceira

class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        mes_selecionado = 0
        ano_selecionado = 0
        if self.request.GET.__contains__("mes_selecionado"):
            dia_selecionado = self.request.GET["dia_selecionado"]
            mes_selecionado = self.request.GET["mes_selecionado"]
            ano_selecionado = self.request.GET["ano_selecionado"]
        else:
            dia_selecionado = timezone.now().day
            mes_selecionado = str(timezone.now().month)
            ano_selecionado = timezone.now().year
        hoje = datetime.now().strftime("%Y-%m-%d")
        venda_lucro_consolidado = 0
        #Campo Resumo Lucro Líquido por Venda
        listarVendasTemplate = []
        identificadorVenda = 0
        lucro_venda = 0
        valor_total_venda = 0
        valor_recebido_venda = 0
        valor_excedente_venda_consolidado = 0
        total_a_receber_consolidado = 0
        valor_total_venda_consolidado = 0
        valor_recebido_venda_consolidado = 0
        quantidade_total_produtos = 0
        #Dados de receita
        vendas = Venda.objects.filter(criados__month=mes_selecionado).filter(criados__year=ano_selecionado).filter(ativo=True).order_by('-id')
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
                logging.warning(venda.identificadorVenda)
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


        #Dados de despesa
        cadastro_despesas = CadastroDespesa.objects.filter(ativo=True).filter(criados__year__lte=ano_selecionado).filter(criados__month__lte=mes_selecionado).filter(criados__day__lte=dia_selecionado)
        despesas_template = []
        mes_anterior = 0
        ano_anterior = 0
        #logging.warning(str(ano_selecionado) + " " + str(mes_selecionado) +" "+str(dia_selecionado))
        for despesa in cadastro_despesas:
            if despesa.periodicidade < 4:
                mes_anterior = mes_selecionado
                ano_anterior = ano_selecionado
            if despesa.periodicidade == 4:
                if mes_selecionado == "1":
                    mes_anterior = 12
                    ano_anterior = ano_selecionado - 1
                else:
                    mes_anterior = int(mes_selecionado) - 1
                    ano_anterior = ano_selecionado
            if despesa.periodicidade == 5:
                if mes_selecionado <= "3":
                    mes_anterior = 13 - (4 - int(mes_selecionado))
                    ano_anterior = ano_selecionado - 1
                else:
                    mes_anterior = int(mes_selecionado) - 3
                    ano_anterior = ano_selecionado
            if despesa.periodicidade == 6:
                if mes_selecionado <= "6":
                    mes_anterior = 13 - (7 - int(mes_selecionado))
                    ano_anterior = ano_selecionado - 1
                else:
                    mes_anterior = int(mes_selecionado) - 6
                    ano_anterior = ano_selecionado
            if despesa.periodicidade == 7:
                mes_anterior = mes_selecionado
                ano_anterior = ano_selecionado - 1
            #logging.warning(str(ano_anterior) + " " + str(mes_anterior))
            verificar_registro_despesa = Despesa.objects.filter(criados__month=mes_anterior).filter(criados__year=ano_anterior).filter(despesa_id=despesa.id).filter(ativo=True).count()
            if verificar_registro_despesa == 0 and despesa.periodicidade > 0:
                conta_em_dolar=0
                cotacao_dolar=0
                data_anterior=""
                tipo_movimentacao = Conta.objects.get(id=despesa.conta_debito_id)
                if tipo_movimentacao.categoria_id > 3:
                    conta_em_dolar = 1
                    valor_dolar = MovimentacaoFinanceira()
                    cotacao_dolar = valor_dolar.dolarMedio()
                else:
                    conta_em_dolar = 0
                    cotacao_dolar = 1
                logging.warning("Entrei")
                data_anterior = datetime(ano_anterior,mes_anterior,1).strftime("%Y-%m-%d")
                registro_movimentacao = MovimentacaoConta(
                    criados=data_anterior,
                    contaDebito=despesa.conta_debito_id,
                    valorDebito=despesa.valor,
                    identificadorCompra=0,
                    identificadorVenda=0,
                    descricao=despesa.nome_despesa,
                    cotacaoDolar=cotacao_dolar,
                    identificadorDolar=conta_em_dolar,
                )
                registro_movimentacao.save()
                conta = Conta.objects.get(id=despesa.conta_debito_id)
                registro_despesa = Despesa(
                    criados=data_anterior,
                    ativo=1,
                    despesa_id=despesa.id,
                    movimentacao_id=registro_movimentacao.id,
                )
                registro_despesa.save()

        despesas = Despesa.objects.filter(ativo=True).filter(modificado__year=ano_selecionado).filter(modificado__month=mes_selecionado)
        valor_despesa_total = 0
        for despesa in despesas:
            conta_debito=0
            moeda=""
            cotacao_dolar=1
            contas = Conta.objects.filter(ativo=True).filter(id=despesa.movimentacao.contaDebito)
            for conta in contas:
                conta_debito = conta.nomeConta
                if despesa.movimentacao.identificadorDolar == 0:
                    moeda="R$"
                else:
                    moeda="US$"
                cotacao_dolar = despesa.movimentacao.cotacaoDolar
            despesas_template.append(
                {
                'id': despesa.id,
                'nome_despesa': despesa.despesa.nome_despesa,
                'data': despesa.modificado,
                'valor': despesa.movimentacao.valorDebito,
                'conta': conta_debito,
                'moeda': moeda
                }
            )
            valor_despesa_total = valor_despesa_total + despesa.movimentacao.valorDebito * cotacao_dolar

        #Cálculo do valor em estoque
        valor_total_estoque = 0
        produtos = Produto.objects.filter(estoque__gt = 0)
        for produto in produtos:
            compras_produto = Compra.objects.filter(produto_id=produto.id, ativo=True).order_by('-id')
            quantidade_produto_estoque = produto.estoque
            for compra in compras_produto:
                if compra.quantidadeProduto >= quantidade_produto_estoque:
                    valor_total_estoque = (valor_total_estoque +
                                            float(compra.precoProduto) * compra.valorDolarMedio * quantidade_produto_estoque)
                    break
                else:
                    valor_total_estoque = (valor_total_estoque +
                                            float(compra.precoProduto) * compra.valorDolarMedio * compra.quantidadeProduto)
                    quantidade_produto_estoque = quantidade_produto_estoque - compra.quantidadeProduto

        #Total de compras no período
        listarComprasTemplate = []
        identificadorCompra = 0
        valor_total_compra = 0
        consolidado_compras_mensal = 0
        compras = Compra.objects.filter(criados__month=mes_selecionado).filter(criados__year=ano_selecionado).filter(ativo=True).order_by('-criados')
        for compra in compras:
            if identificadorCompra != compra.identificadorCompra:
                #Valor total das compras
                compra_identificada = Compra.objects.filter(identificadorCompra=compra.identificadorCompra,ativo=True)
                for compra in compra_identificada:
                    valor_total_compra = valor_total_compra + compra.quantidadeProduto * compra.precoProduto * compra.valorDolarMedio
                #Calculando os fretes
                itinerario = Deslocamento.objects.filter(identificadorCompra=compra.identificadorCompra,ativo=True)
                valor_frete = 0
                for cidade in itinerario:
                    frete_deslocamento = MovimentacaoConta.objects.filter(id=cidade.idMovimentacaoConta, ativo=True)
                    for valor_deslocamento in frete_deslocamento:
                        if valor_deslocamento.identificadorDolar == True:
                            valor_frete = valor_frete + valor_deslocamento.valorDebito * valor_deslocamento.cotacaoDolar
                        else:
                            valor_frete = valor_frete + valor_deslocamento.valorDebito
                valor_total_compra = valor_total_compra + valor_frete
                listarComprasTemplate.append(
                    {
                     'compra_id': compra.identificadorCompra,
                     'nome_fornecedor': compra.fornecedor.nomeFornecedor,
                     'data_compra': compra.criados,
                     'valor_total_compra': valor_total_compra,
                     'moeda': moeda
                     }
                )
                consolidado_compras_mensal = consolidado_compras_mensal + valor_total_compra
                valor_total_compra = 0
                valor_frete = 0
                identificadorCompra = compra.identificadorCompra

        context['vendas'] = listarVendasTemplate
        context['venda_lucro_total'] = venda_lucro_consolidado
        context['despesas'] = despesas_template
        context['valor_total_venda'] = valor_total_venda_consolidado
        context['valor_recebido_venda'] = valor_recebido_venda_consolidado
        context['total_a_receber'] = total_a_receber_consolidado
        context['valor_excedente_venda'] = valor_excedente_venda_consolidado
        context['compras'] = listarComprasTemplate
        context['consolidado_compras'] = consolidado_compras_mensal
        context['valor_despesa_total'] = valor_despesa_total
        context['saldo_liquido_mensal'] = venda_lucro_consolidado - valor_despesa_total
        if quantidade_total_produtos > 0:
            context['ticket_medio'] = valor_total_venda_consolidado / quantidade_total_produtos
        else:
            context['ticket_medio'] = 0
        context['valor_total_estoque'] = valor_total_estoque
        return context