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
        if self.request.GET.__contains__("idDespesa"):
            if self.request.GET["funcao"] == "apagar":
                CadastroDespesa.objects.filter(id=self.request.GET["idDespesa"]).update(ativo=False)
                context["mensagem"] = "Despesa Apagada"
        contasDetalhadas = Conta.objects.all()
        conta_despesa = []
        for conta in contasDetalhadas:
            conta_despesa.append({'id': conta.id, 'nomeConta': conta.nomeConta})

        context['conta_despesa'] = conta_despesa
        context['despesas'] = self.despesas_cadastradas()
        #context["categoria"] = CategoriaConta.objects.all()
        #context["mensagem"] = ""
        return context

    def post(self, request, *args, **kwargs):
        context = super(AdicionarDespesa, self).get_context_data(**kwargs)
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
            contasDetalhadas = Conta.objects.all()
            conta_despesa = []
            for conta in contasDetalhadas:
                conta_despesa.append({'id': conta.id, 'nomeConta': conta.nomeConta})
            context['conta_despesa'] = conta_despesa
            context['despesas'] = self.despesas_cadastradas()
            context['mensagem'] = "Despesa Salva"
        return super(TemplateView, self).render_to_response(context)

    def despesas_cadastradas(self):
        despesas_cadastradas = CadastroDespesa.objects.filter(ativo=True).order_by('-id')
        despesas_template = []
        for despesa in despesas_cadastradas:
            conta_debito = 0
            moeda = ""
            cotacao_dolar = 1
            contas = Conta.objects.filter(ativo=True).filter(id=despesa.conta_debito_id)
            for conta in contas:
                conta_debito = conta.nomeConta
                if conta.categoria_id >=1 and conta.categoria_id <= 3:
                    moeda = "R$"
                else:
                    moeda = "US$"
            logging.warning("Nome Conta")
            logging.warning(conta_debito)
            despesas_template.append(
                {
                    'id': despesa.id,
                    'nome_despesa': despesa.nome_despesa,
                    'data': despesa.criados,
                    'valor': despesa.valor,
                    'conta': conta_debito,
                    'moeda': moeda
                }
            )
        return(despesas_template)
# Create your views here.
