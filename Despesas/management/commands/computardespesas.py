from django.core.management.base import BaseCommand
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

class Command(BaseCommand):
    help = 'Computa despesas'

    def handle(self, *args, **kwargs):
        print("Rodando cálculo de despesas...")
        dia_selecionado = timezone.now().day
        mes_selecionado = str(timezone.now().month)
        ano_selecionado = timezone.now().year
        hoje = datetime.now().strftime("%Y-%m-%d")
        #Dados de despesa
        cadastro_despesas = CadastroDespesa.objects.filter(ativo=True).filter(periodicidade__gt=0)#.filter(criados__year__lte=ano_selecionado).filter(criados__month__lte=mes_selecionado).filter(criados__day__lte=dia_selecionado)
        despesas_template = []
        mes_anterior = 0
        ano_anterior = 0
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

            verificar_registro_despesa = Despesa.objects.filter(
                criados__month=mes_anterior
            ).filter(
                criados__year=ano_anterior
            ).filter(
                despesa_id=despesa.id
            ).filter(
                ativo=True
            ).count()

            if verificar_registro_despesa == 0 and despesa.periodicidade > 0:
                conta_em_dolar=0
                cotacao_dolar=0
                data_anterior=""
                tipo_movimentacao = Conta.objects.get(id=despesa.conta_debito_id)
                if tipo_movimentacao.categoria_id > 3:
                    conta_em_dolar = 1
                    valor_dolar = MovimentacaoFinanceira(0,0)
                    cotacao_dolar = valor_dolar.dolarMedio()
                else:
                    conta_em_dolar = 0
                    cotacao_dolar = 1
                logging.warning("Entrei")
                data_anterior = datetime(int(ano_anterior),int(mes_anterior),1).strftime("%Y-%m-%d")
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

