from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages


from Despesas.models import CadastroDespesa, Despesa
from Contas.models import Conta, MovimentacaoConta
from Contas.views import MovimentacaoFinanceira
from datetime import date, datetime
import re
import logging
from django.utils import timezone


class AdicionarDespesa(TemplateView):
    template_name = "adicionardespesa.html"

    def get_context_data(self, **kwargs):
        context = super(AdicionarDespesa, self).get_context_data(**kwargs)
        contasDetalhadas = Conta.objects.all()
        conta_despesa = []
        for conta in contasDetalhadas:
            conta_despesa.append({'id': conta.id, 'nomeConta': conta.nomeConta})

        context['conta_despesa'] = conta_despesa

        #context["categoria"] = CategoriaConta.objects.all()
        #context["mensagem"] = ""
        return context

    def post(self, request, *args, **kwargs):
        data_modificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', self.request.POST.get("data_despesa"))
        conta_em_dolar = 0
        cotacao_dolar = 0
        tipo_movimentacao = Conta.objects.get(id=self.request.POST.get("conta_despesa"))
        if tipo_movimentacao.categoria_id > 3:
            conta_em_dolar = 1
            valor_dolar = MovimentacaoFinanceira()
            cotacao_dolar = valor_dolar.dolarMedio()
        else:
            conta_em_dolar = 0
            cotacao_dolar = 1

        dataform_despesa = CadastroDespesa(
            criados= data_modificada,
            nome_despesa=self.request.POST.get("nome_despesa"),
            periodicidade=self.request.POST.get("periodicidade"),
            valor=self.request.POST.get("valor_despesa"),
            conta_debito_id=self.request.POST.get("conta_despesa"),
        )
        dataform_despesa.save()
        if self.request.POST.get("periodicidade") == "0":
            registro_movimentacao = MovimentacaoConta(
                criados=data_modificada,
                contaDebito=self.request.POST.get("conta_despesa"),
                valorDebito=self.request.POST.get("valor_despesa"),
                identificadorCompra=0,
                identificadorVenda=0,
                descricao=self.request.POST.get("nome_despesa"),
                cotacaoDolar=cotacao_dolar,
                identificadorDolar=conta_em_dolar,
            )
            registro_movimentacao.save()
            registro_despesa = Despesa(
                criados=data_modificada,
                ativo=1,
                despesa_id=dataform_despesa.id,
                movimentacao_id=registro_movimentacao.id,
            )
            registro_despesa.save()
        #context = super(EditarContaView, self).get_context_data(**kwargs)
        #context["conta"] = Conta.objects.all()
        #context["ategoriaconta"] = CategoriaConta.objects.all()
        return HttpResponseRedirect("/adicionardespesa/?despesacadastrada=1")

# Create your views here.
