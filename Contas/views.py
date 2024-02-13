import logging
import re
from datetime import date, datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from Compras.models import Fornecedor
from Vendas.models import Cliente, Venda

from .models import Cartao, CategoriaConta, Conta, MovimentacaoConta


class CriarContaView(TemplateView):
    template_name = "addaccount.html"

    def get_context_data(self, **kwargs):
        context = super(CriarContaView, self).get_context_data(**kwargs)
        context["categoria"] = CategoriaConta.objects.all()
        context["mensagem"] = ""
        return context

    def post(self, request, *args, **kwargs):
        try:
            ultima_conta = Cartao.objects.last()
            proxima_conta = ultima_conta.cartao + 1
            logging.warning(proxima_conta)
        except:
            proxima_conta = 1
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        logging.warning(proxima_conta)
        if self.request.POST.get("categoria") == "1":
            dataform_cartao = Cartao(
                criados=hoje,
                taxa_debito=self.request.POST.get("taxa_debito"),
                taxa_cartao1=self.request.POST.get("taxa1"),
                taxa_cartao2=self.request.POST.get("taxa2"),
                taxa_cartao3=self.request.POST.get("taxa3"),
                taxa_cartao4=self.request.POST.get("taxa4"),
                taxa_cartao5=self.request.POST.get("taxa5"),
                taxa_cartao6=self.request.POST.get("taxa6"),
                taxa_cartao7=self.request.POST.get("taxa7"),
                taxa_cartao8=self.request.POST.get("taxa8"),
                taxa_cartao9=self.request.POST.get("taxa9"),
                taxa_cartao10=self.request.POST.get("taxa10"),
                taxa_cartao11=self.request.POST.get("taxa11"),
                taxa_cartao12=self.request.POST.get("taxa12"),
                taxa_cartao13=self.request.POST.get("taxa13"),
                taxa_cartao14=self.request.POST.get("taxa14"),
                taxa_cartao15=self.request.POST.get("taxa15"),
                taxa_cartao16=self.request.POST.get("taxa16"),
                taxa_cartao17=self.request.POST.get("taxa17"),
                taxa_cartao18=self.request.POST.get("taxa18"),
                cartao=proxima_conta,
            )
            dataform_cartao.save()

            dataform_conta = Conta(
                nomeConta=self.request.POST.get("nomeConta"),
                criados=hoje,
                categoria_id=self.request.POST.get("categoria"),
                descricao=self.request.POST.get("descricao"),
                taxas=0,
                cartao=proxima_conta,
            )
            dataform_conta.save()

            agora = datetime.now()
            hoje = agora.strftime("%Y-%m-%d")
            dataform_movimentacaoconta = MovimentacaoConta(
                criados=hoje,
                contaCredito_id=dataform_conta.id,
                valorCredito=self.request.POST.get("saldoinicial"),
                descricao="Saldo Inicial",
                identificadorDolar="0",
            )
            dataform_movimentacaoconta.save()
        else:
            dataform_conta = Conta(
                nomeConta=self.request.POST.get("nomeConta"),
                criados=hoje,
                categoria_id=self.request.POST.get("categoria"),
                descricao=self.request.POST.get("descricao"),
                taxas=self.request.POST.get("taxas"),
                taxa_wire=self.request.POST.get("wire"),
                valor_dolar_medio=self.request.POST.get("valordolarmedio"),
            )
            dataform_conta.save()

            identificadorDolar = 0
            if ((self.request.POST.get("categoria") == "4") or (self.request.POST.get("categoria") == "5")):
                identificadorDolar = 1

            agora = datetime.now()
            hoje = agora.strftime("%Y-%m-%d")
            dataform_movimentacaoconta = MovimentacaoConta(
                criados=hoje,
                contaCredito_id=dataform_conta.id,
                valorCredito=self.request.POST.get("saldoinicial"),
                descricao="Saldo Inicial",
                cotacaoDolar=self.request.POST.get("valordolarmedio"),
                identificadorDolar=identificadorDolar,
            )
            dataform_movimentacaoconta.save()

        context = super(CriarContaView, self).get_context_data(**kwargs)
        context["mensagem"] = "Conta Salva"
        context["categoria"] = CategoriaConta.objects.all()
        return super(TemplateView, self).render_to_response(context)


class ListarContaView(TemplateView):
    template_name = "accountlist.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["mensagem"] = ""
        if self.request.GET.__contains__("idConta"):
            if self.request.GET["funcao"] == "apagar":
                apagarconta = Conta(id=self.request.GET["idConta"])
                apagarconta.delete()
        if self.request.GET.__contains__("contacadastrada"):
            context["mensagem"] = "Conta Salva"
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ListarContaView, self).get_context_data(**kwargs)
        context["contas"] = Conta.objects.filter(id__gt = 0)
        context["categoriaconta"] = CategoriaConta.objects.all()
        return context


class EditarContaView(TemplateView):
    template_name = "editaccount.html"

    def get_context_data(self, **kwargs):
        context = super(EditarContaView, self).get_context_data(**kwargs)
        context["categoria"] = CategoriaConta.objects.all()
        context["contaselecionada"] = Conta.objects.get(id=self.request.GET["idConta"])
        try:
            context["taxas_cartao"] = Cartao.objects.get(cartao=context["contaselecionada"].cartao)
        except:
            pass
        context["contaselecionada"].taxas = str(
            float(context["contaselecionada"].taxas)
        )
        #context["contaselecionada"].valorCredito = str(
        #    float(context["contaselecionada"].valorCredito)
        #)
        context["categoriacontaselecionada"] = CategoriaConta.objects.get(
            categoria=context["contaselecionada"].categoria
        )
        context["mensagem"] = ""
        return context


    def post(self, request, *args, **kwargs):
        dataform = Conta.objects.get(id=self.request.POST.get("idConta"))
        dataform.nomeConta = self.request.POST.get("nomeConta")
        dataform.categoria_id = self.request.POST.get("categoria")
        dataform.taxas = self.request.POST.get("taxas")
        dataform.descricao = self.request.POST.get("descricao")
        dataform.saldoInicial = self.request.POST.get("saldoinicial")
        dataform.save()

        if self.request.POST.get("cartao") != "":
            cartao = Cartao.objects.get(cartao=self.request.POST.get("cartao"))
            cartao.taxa_debito = self.request.POST.get("taxa_debito")
            cartao.taxa_cartao1 = self.request.POST.get("taxa1")
            cartao.taxa_cartao2 = self.request.POST.get("taxa2")
            cartao.taxa_cartao3 = self.request.POST.get("taxa3")
            cartao.taxa_cartao4 = self.request.POST.get("taxa4")
            cartao.taxa_cartao5 = self.request.POST.get("taxa5")
            cartao.taxa_cartao6 = self.request.POST.get("taxa6")
            cartao.taxa_cartao7 = self.request.POST.get("taxa7")
            cartao.taxa_cartao8 = self.request.POST.get("taxa8")
            cartao.taxa_cartao9 = self.request.POST.get("taxa9")
            cartao.taxa_cartao10 = self.request.POST.get("taxa10")
            cartao.taxa_cartao11 = self.request.POST.get("taxa11")
            cartao.taxa_cartao12 = self.request.POST.get("taxa12")
            cartao.taxa_cartao13 = self.request.POST.get("taxa13")
            cartao.taxa_cartao14 = self.request.POST.get("taxa14")
            cartao.taxa_cartao15 = self.request.POST.get("taxa15")
            cartao.taxa_cartao16 = self.request.POST.get("taxa16")
            cartao.taxa_cartao17 = self.request.POST.get("taxa17")
            cartao.taxa_cartao18 = self.request.POST.get("taxa18")
            cartao.save()

        #context = super(EditarContaView, self).get_context_data(**kwargs)
        #context["conta"] = Conta.objects.all()
        #context["categoriaconta"] = CategoriaConta.objects.all()
        return HttpResponseRedirect("/listarconta/?contacadastrada=1")


class ComprarDolarView(TemplateView):
    template_name = "compradolar.html"

    def get_context_data(self, **kwargs):
        context = super(ComprarDolarView, self).get_context_data(**kwargs)
        context["mensagem"] = ""
        if self.request.GET.__contains__("idMovimento"):
            if self.request.GET["funcao"] == "apagar":
                apagarproduto = MovimentacaoConta(id=self.request.GET["idMovimento"])
                apagarproduto.delete()
                context["mensagem"] = "Conta Apagada"

        # Popular template
        informacoes_financeiras = MovimentacaoFinanceira()
        context["cartaoCreditoValorTotal"] = informacoes_financeiras.valores_cartao_credito
        context["especieValorTotal"] = informacoes_financeiras.valores_especie
        context["depositoRealValorTotal"] = informacoes_financeiras.valores_conta_real
        context["depositoDolarValorTotal"] = informacoes_financeiras.valores_dolar
        context["depositoDolarPyValorTotal"] = informacoes_financeiras.valores_dolar_paraguai

        # Popular template com dados de conta
        contas = informacoes_financeiras.contas_origem_e_detalhadas()
        context["contasDetalhadas"] = contas["contasDetalhadasTemplate"]
        context["contaOrigem"] = contas["contaOrigem"]
        context["contaDestino"] = contas["contaDestino"]

        # popular movimentações
        context["movimentacaoContas"] = informacoes_financeiras.movimentacoes_contas

        return context

    def post(self, request, *args, **kwargs):
        context = super(ComprarDolarView, self).get_context_data(**kwargs)
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        dataform = MovimentacaoConta(
            contaCredito_id=self.request.POST.get("contaDestino"),
            contaDebito=self.request.POST.get("contaOrigem"),
            valorCredito=float(self.request.POST.get("valorReal"))
            / float(self.request.POST.get("cotacao")),
            valorDebito=self.request.POST.get("valorReal"),
            criados=hoje,
            cotacaoDolar=float(self.request.POST.get("cotacao")),
            identificadorDolar=True,
        )
        dataform.save()
        context["mensagem"] = "Compra Efetuada"
        # Popular template
        informacoes_financeiras = MovimentacaoFinanceira()
        context["cartaoCreditoValorTotal"] = informacoes_financeiras.valores_cartao_credito
        context["especieValorTotal"] = informacoes_financeiras.valores_especie
        context["depositoRealValorTotal"] = informacoes_financeiras.valores_conta_real
        context["depositoDolarValorTotal"] = informacoes_financeiras.valores_dolar
        context["depositoDolarPyValorTotal"] = informacoes_financeiras.valores_dolar_paraguai

        # Popular template com dados de conta
        contas = informacoes_financeiras.contas_origem_e_detalhadas()
        context["contasDetalhadas"] = contas["contasDetalhadasTemplate"]
        context["contaOrigem"] = contas["contaOrigem"]

        # popular movimentações
        context["movimentacaoContas"] = informacoes_financeiras.movimentacoes_contas


        return super(TemplateView, self).render_to_response(context)


class AdicionarFundosView(TemplateView):
    template_name = "adicionarfundos.html"

    def get_context_data(self, **kwargs):
        context = super(AdicionarFundosView, self).get_context_data(**kwargs)
        context["mensagem"] = ""
        if self.request.GET.__contains__("idMovimento"):
            if self.request.GET["funcao"] == "apagar":
                apagarproduto = MovimentacaoConta(id=self.request.GET["idMovimento"])
                apagarproduto.delete()
                context["mensagem"] = "Movimento Financeiro Apagado"

        # Popular template
        informacoes_financeiras = MovimentacaoFinanceira()
        context["cartaoCreditoValorTotal"] = informacoes_financeiras.valores_cartao_credito
        context["especieValorTotal"] = informacoes_financeiras.valores_especie
        context["depositoRealValorTotal"] = informacoes_financeiras.valores_conta_real
        context["depositoDolarValorTotal"] = informacoes_financeiras.valores_dolar
        context["depositoDolarPyValorTotal"] = informacoes_financeiras.valores_dolar_paraguai

        # Popular template com dados de conta
        contas = informacoes_financeiras.contas_origem_e_detalhadas()
        context["contasDetalhadas"] = contas["contasDetalhadasTemplate"]
        context["contaOrigem"] = contas["contaOrigem"]

        # popular movimentações
        context["movimentacaoContas"] = informacoes_financeiras.movimentacoes_contas

        return context

    def post(self, request, *args, **kwargs):
        context = super(AdicionarFundosView, self).get_context_data(**kwargs)
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        dataform = MovimentacaoConta(
            contaCredito_id=self.request.POST.get("contaOrigem"),
            contaDebito="0",
            valorCredito=self.request.POST.get("valorReal"),
            valorDebito="0",
            criados=hoje,
            identificadorDolar="0",
        )
        dataform.save()
        context["mensagem"] = "Aporte Efetuado"

        # Popular template
        informacoes_financeiras = MovimentacaoFinanceira()
        context["cartaoCreditoValorTotal"] = informacoes_financeiras.valores_cartao_credito
        context["especieValorTotal"] = informacoes_financeiras.valores_especie
        context["depositoRealValorTotal"] = informacoes_financeiras.valores_conta_real
        context["depositoDolarValorTotal"] = informacoes_financeiras.valores_dolar
        context["depositoDolarPyValorTotal"] = informacoes_financeiras.valores_dolar_paraguai

        # Popular template com dados de conta
        contas = informacoes_financeiras.contas_origem_e_detalhadas()
        context["contasDetalhadas"] = contas["contasDetalhadasTemplate"]
        context["contaOrigem"] = contas["contaOrigem"]

        # popular movimentações
        context["movimentacaoContas"] = informacoes_financeiras.movimentacoes_contas

        return super(TemplateView, self).render_to_response(context)
class RetiradaView(TemplateView):
    template_name = "retirada.html"

    def get_context_data(self, **kwargs):
        context = super(RetiradaView, self).get_context_data(**kwargs)
        context["mensagem"] = ""
        if self.request.GET.__contains__("idMovimento"):
            if self.request.GET["funcao"] == "apagar":
                apagarproduto = MovimentacaoConta(id=self.request.GET["idMovimento"])
                apagarproduto.delete()
                context["mensagem"] = "Conta Apagada"

        # Popular template
        informacoes_financeiras = MovimentacaoFinanceira()
        context["cartaoCreditoValorTotal"] = informacoes_financeiras.valores_cartao_credito
        context["especieValorTotal"] = informacoes_financeiras.valores_especie
        context["depositoRealValorTotal"] = informacoes_financeiras.valores_conta_real
        context["depositoDolarValorTotal"] = informacoes_financeiras.valores_dolar
        context["depositoDolarPyValorTotal"] = informacoes_financeiras.valores_dolar_paraguai

        # Popular template com dados de conta
        contas = informacoes_financeiras.contas_origem_e_detalhadas()
        context["contasDetalhadas"] = contas["contasDetalhadasTemplate"]
        context["contaOrigem"] = contas["contaOrigem"]
        # popular movimentações
        context["movimentacaoContas"] = informacoes_financeiras.movimentacoes_contas

        return context

    def post(self, request, *args, **kwargs):
        context = super(RetiradaView, self).get_context_data(**kwargs)
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        dataform = MovimentacaoConta(
            contaCredito_id="0",
            contaDebito=self.request.POST.get("contaOrigem"),
            valorCredito="0",
            valorDebito=self.request.POST.get("valorReal"),
            criados=hoje,
            descricao="Retirada",
            identificadorDolar="0",
        )
        dataform.save()
        context["mensagem"] = "Retirada Efetuada"

        # Popular template
        informacoes_financeiras = MovimentacaoFinanceira()
        context["cartaoCreditoValorTotal"] = informacoes_financeiras.valores_cartao_credito
        context["especieValorTotal"] = informacoes_financeiras.valores_especie
        context["depositoRealValorTotal"] = informacoes_financeiras.valores_conta_real
        context["depositoDolarValorTotal"] = informacoes_financeiras.valores_dolar
        context["depositoDolarPyValorTotal"] = informacoes_financeiras.valores_dolar_paraguai

        # Popular template com dados de conta
        contas = informacoes_financeiras.contas_origem_e_detalhadas()
        context["contasDetalhadas"] = contas["contasDetalhadasTemplate"]
        context["contaOrigem"] = contas["contaOrigem"]

        # popular movimentações
        context["movimentacaoContas"] = informacoes_financeiras.movimentacoes_contas

        return super(TemplateView, self).render_to_response(context)
class ListarMovimentacoesView(TemplateView):
    template_name = "listarmovimentacoes.html"
    def get_context_data(self, **kwargs):
        context = super(ListarMovimentacoesView, self).get_context_data(**kwargs)
        context["mensagem"] = ""
        if self.request.GET.__contains__("idMovimento"):
            if self.request.GET["funcao"] == "apagar":
                apagarmovimentacao = MovimentacaoConta(id=self.request.GET["idMovimento"])
                apagarmovimentacao.delete()
                context["mensagem"] = "Movimentação Apagada"
        # popular movimentações
        context["movimentacaoContas"] = self.movimentacoes_contas
        return context
    def movimentacoes_contas(self):
        movimentacaoConta = MovimentacaoConta.objects.all().order_by('-id')
        movimentacaoContasTemplate = []
        for movimentacao in movimentacaoConta:
            nome_conta_credito = "Conta não identificada"
            nome_conta_debito = "Saldo Inicial"
            # Se for uma movimentação de compra ou venda não listar
            try:
                contaCredito = Conta.objects.get(id=movimentacao.contaCredito_id)
                nome_conta_credito = contaCredito.nomeConta
            except:
                pass
            try:
                contaDebito = Conta.objects.get(id=movimentacao.contaDebito)
                nome_conta_debito = contaDebito.nomeConta
            except:
                pass
            logging.warning(movimentacao.id)
            if movimentacao.identificadorCompra == 0 and movimentacao.identificadorVenda == 0:
                movimentacaoContasTemplate.append(
                {
                    "data": movimentacao.criados,
                    "contaOrigem": nome_conta_debito,
                    "contaDestino": nome_conta_credito,
                    "valorContaOrigem": movimentacao.valorDebito,
                    "valorContaDestino": movimentacao.valorCredito,
                    "idMovimento": movimentacao.id,
                }
                )
        return movimentacaoContasTemplate

class MovimentacaoFinanceira:
    def valores_cartao_credito(self):
        cartaoCredito = Conta.objects.filter(categoria_id=1)
        cartaoCreditoValorTotal = 0
        for cartaoCreditoValor in cartaoCredito:
            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(
                contaCredito=cartaoCreditoValor.id
            )
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal + conta.valorCredito

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(
                contaDebito=cartaoCreditoValor.id
            )
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal - conta.valorDebito

        return cartaoCreditoValorTotal

    def valores_especie(self):
        especie = Conta.objects.filter(categoria_id=3).filter(id__gt=0)
        especieValorTotal = 0
        for especieValor in especie:
            #especieValorTotal = especieValorTotal + especieValor.saldoInicial
            especieMovimento = MovimentacaoConta.objects.filter(
                contaCredito=especieValor.id
            )
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal + conta.valorCredito

            especieMovimento = MovimentacaoConta.objects.filter(
                contaDebito=especieValor.id
            )
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal - conta.valorDebito

        return especieValorTotal

    def valores_conta_real(self):
        depositoReal = Conta.objects.filter(categoria_id=2)
        depositoRealValorTotal = 0
        for depositoRealValor in depositoReal:
            depositoRealMovimento = MovimentacaoConta.objects.filter(
                contaCredito=depositoRealValor.id
            )
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal + conta.valorCredito

            depositoRealMovimento = MovimentacaoConta.objects.filter(
                contaDebito=depositoRealValor.id
            )
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal - conta.valorDebito

        return depositoRealValorTotal

    def valores_dolar(self):
        depositoDolar = Conta.objects.filter(categoria_id=4)
        depositoDolarValorTotal = 0
        for depositoDolarValor in depositoDolar:
            #depositoDolarValorTotal = (
            #    depositoDolarValorTotal + depositoDolarValor.saldoInicial
            #)

            depositoDolarMovimento = MovimentacaoConta.objects.filter(
                contaCredito=depositoDolarValor.id
            )
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal + conta.valorCredito

            depositoDolarMovimento = MovimentacaoConta.objects.filter(
                contaDebito=depositoDolarValor.id
            )
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal - conta.valorDebito

        return depositoDolarValorTotal

    def valores_dolar_paraguai(self):
        depositoDolarPy = Conta.objects.filter(categoria_id=5)
        depositoDolarPyValorTotal = 0
        for depositoDolarPyValor in depositoDolarPy:
            depositoDolarPyValorTotal = (
                depositoDolarPyValorTotal + depositoDolarPyValor.saldoInicial
            )

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(
                contaCredito=depositoDolarPyValor.id
            )
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = (
                    depositoDolarPyValorTotal + conta.valorCredito
                )

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(
                contaDebito=depositoDolarPyValor.id
            )
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = (
                    depositoDolarPyValorTotal - conta.valorDebito
                )

        return depositoDolarPyValorTotal

    def movimentacoes_contas(self):
        movimentacaoConta = MovimentacaoConta.objects.all()[:10]
        movimentacaoContasTemplate = []

        for conta in movimentacaoConta:
            # Se for uma movimentação de compra ou venda ou movimentação entre contas não listar
            if conta.identificadorCompra == 0 and conta.identificadorVenda == 0:
                contaCredito = Conta.objects.get(id=conta.contaCredito_id)
                movimentacaoContasTemplate.append(
                    {
                        "data": conta.criados,
                        "contaOrigem": contaCredito.nomeConta,
                        "valorContaOrigem": conta.valorCredito,
                        "idMovimento": conta.id,
                    }
                )
        # popular movimentações
        #context["movimentacaoContas"] = self.movimentacoes_contas
        return movimentacaoContasTemplate

    def contas_origem_e_detalhadas(self):
        contasDetalhadas = Conta.objects.all().filter(id__gt=0)
        contasDetalhadasTemplate = []
        contaOrigem = []
        contaDestino = []
        saldoConta = 0
        for conta in contasDetalhadas:
            #saldoConta = conta.saldoInicial
            entradas = MovimentacaoConta.objects.filter(contaCredito=conta.id)

            for entrada in entradas:
                saldoConta = saldoConta + entrada.valorCredito

            saidas = MovimentacaoConta.objects.filter(contaDebito=conta.id)

            for saida in saidas:
                saldoConta = saldoConta - saida.valorDebito

            if conta.categoria_id <= 3 and conta.categoria_id >= 1:
                moeda = "R$"
                contaOrigem.append({"id": conta.id, "nomeConta": conta.nomeConta})
            else:
                moeda = "US$"
                contaDestino.append({"id": conta.id, "nomeConta": conta.nomeConta})



            contasDetalhadasTemplate.append(
                {"nomeConta": conta.nomeConta, "saldo": saldoConta, "moeda": moeda}
            )

            saldoConta = 0


        return {
                "contaOrigem": contaOrigem,
                "contasDetalhadasTemplate": contasDetalhadasTemplate,
                "contaDestino": contaDestino
        }

    def saldo_conta(self):
        # Buscar saldo em contas
        contasDetalhadas = Conta.objects.all()
        contasDetalhadasTemplate = []

        for conta in contasDetalhadas:
            saldoConta = 0
            entradas = MovimentacaoConta.objects.filter(contaCredito=conta.id)

            for entrada in entradas:
                saldoConta = saldoConta + entrada.valorCredito

            saidas = MovimentacaoConta.objects.filter(contaDebito=conta.id)

            for saida in saidas:
                saldoConta = saldoConta - saida.valorDebito

            if conta.categoria_id <= 3 and conta.categoria_id >= 1:
                moeda = 'R$'
            else:
                moeda = 'US$'

            contasDetalhadasTemplate.append(
                {'nomeConta': conta.nomeConta, 'saldo': saldoConta, 'moeda': moeda, 'id': conta.id})

        return(contasDetalhadasTemplate)

    def dolarMedio(self):
        #Compras em moeda de dólar
        comprasDolar = MovimentacaoConta.objects.filter(identificadorDolar=True, identificadorCompra=0)
        #Compras efetuadas em dólar
        movimentacoesCompra = MovimentacaoConta.objects.filter(identificadorDolar=True, identificadorCompra__gt=0)

        #total em dólares de compras de produtos feitas em dólar
        totalCompraDolar = 0
        for movimentacao in movimentacoesCompra:
            totalCompraDolar = totalCompraDolar + movimentacao.valorDebito - movimentacao.valorCredito
        #Diminuir o total da compra de moeda em dólares das compras de produtos feitas em dólar. A partir daí tirar o dólar médio
        creditoRemanescente = 0
        somaValorReal = 0
        for compra in comprasDolar:
            logging.warning("Total Compra Dólar x Valor Crédito")
            logging.warning(totalCompraDolar)
            logging.warning(compra.valorCredito)
            logging.warning("===================")
            totalCompraDolar = totalCompraDolar - compra.valorCredito
            if totalCompraDolar < 0:
                creditoRemanescente = creditoRemanescente + (-1) * totalCompraDolar
                somaValorReal = somaValorReal + (-1) * totalCompraDolar * compra.cotacaoDolar
                totalCompraDolar = 0

        logging.warning("Soma Valor REal x Credito Remanescente")
        logging.warning(somaValorReal)
        logging.warning(creditoRemanescente)
        logging.warning("===================")

        if creditoRemanescente > 0:
            valorDolarMedio = somaValorReal / creditoRemanescente
        else:
            valorDolarMedio = -1
        return(valorDolarMedio)