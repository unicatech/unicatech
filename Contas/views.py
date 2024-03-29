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
        context["contas"] = Conta.objects.all()
        context["categoriaconta"] = CategoriaConta.objects.all()
        return context


class EditarContaView(TemplateView):
    template_name = "editaccount.html"

    def get_context_data(self, **kwargs):
        context = super(EditarContaView, self).get_context_data(**kwargs)
        context["categoria"] = CategoriaConta.objects.all()
        context["contaselecionada"] = Conta.objects.get(id=self.request.GET["idConta"])
        context["contaselecionada"].taxas = str(
            float(context["contaselecionada"].taxas)
        )
        context["contaselecionada"].saldoInicial = str(
            float(context["contaselecionada"].saldoInicial)
        )
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
        context = super(EditarContaView, self).get_context_data(**kwargs)
        context["conta"] = Conta.objects.all()
        context["categoriaconta"] = CategoriaConta.objects.all()
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

        # Popular template com dados de conta
        cartaoCredito = Conta.objects.filter(categoria_id=1)
        especie = Conta.objects.filter(categoria_id=3)
        depositoReal = Conta.objects.filter(categoria_id=2)
        depositoDolar = Conta.objects.filter(categoria_id=4)
        depositoDolarPy = Conta.objects.filter(categoria_id=5)
        contasDetalhadas = Conta.objects.all()

        cartaoCreditoValorTotal = 0
        for cartaoCreditoValor in cartaoCredito:
            #cartaoCreditoValorTotal = (
            #    cartaoCreditoValorTotal + cartaoCreditoValor.saldoInicial
            #)

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

        depositoRealValorTotal = 0
        for depositoRealValor in depositoReal:
            #depositoRealValorTotal = (
            #    depositoRealValorTotal + depositoRealValor.saldoInicial
            #)

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

        depositoDolarPyValorTotal = 0
        for depositoDolarPyValor in depositoDolarPy:
            #depositoDolarPyValorTotal = (
            #    depositoDolarPyValorTotal + depositoDolarPyValor.saldoInicial
            #)

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

        context["cartaoCreditoValorTotal"] = cartaoCreditoValorTotal
        context["especieValorTotal"] = especieValorTotal
        context["depositoRealValorTotal"] = depositoRealValorTotal
        context["depositoDolarValorTotal"] = depositoDolarValorTotal
        context["depositoDolarPyValorTotal"] = depositoDolarPyValorTotal

        contasDetalhadasTemplate = []
        contaOrigem = []
        contaDestino = []

        for conta in contasDetalhadas:
            #saldoConta = conta.saldoInicial
            saldoConta = 0
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

        context["contasDetalhadas"] = contasDetalhadasTemplate
        context["contaOrigem"] = contaOrigem
        context["contaDestino"] = contaDestino

        # popular movimentações

        movimentacaoConta = MovimentacaoConta.objects.all()
        movimentacaoContasTemplate = []
        for movimentacao in movimentacaoConta:
            nome_conta_credito = "Conta não identificada"
            nome_conta_debito = "Saldo Inicial"
            # Se for uma movimentação de compra ou venda não listar
            try:
                logging.warning(movimentacao.contaCredito_id)
                contaCredito = Conta.objects.get(id=movimentacao.contaCredito_id)
                nome_conta_credito = contaCredito.nomeConta
            except:
                pass
            try:
                contaDebito = Conta.objects.get(id=movimentacao.contaDebito)
                nome_conta_debito = contaDebito.nomeConta
            except:
                pass

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
        context["movimentacaoContas"] = movimentacaoContasTemplate

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
        # Popular template com dados de conta
        cartaoCredito = Conta.objects.filter(categoria_id=1)
        especie = Conta.objects.filter(categoria_id=3)
        depositoReal = Conta.objects.filter(categoria_id=2)
        depositoDolar = Conta.objects.filter(categoria_id=4)
        depositoDolarPy = Conta.objects.filter(categoria_id=5)
        contasDetalhadas = Conta.objects.all()

        cartaoCreditoValorTotal = 0
        for cartaoCreditoValor in cartaoCredito:
            #cartaoCreditoValorTotal = (
            #    cartaoCreditoValorTotal + cartaoCreditoValor.saldoInicial
            #)

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

        depositoRealValorTotal = 0
        for depositoRealValor in depositoReal:
            #depositoRealValorTotal = (
            #    depositoRealValorTotal + depositoRealValor.saldoInicial
            #)

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

        depositoDolarValorTotal = 0
        for depositoDolarValor in depositoDolar:
            #depositoDolarValorTotal = (
            #   depositoDolarValorTotal + depositoDolarValor.saldoInicial
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

        depositoDolarPyValorTotal = 0
        for depositoDolarPyValor in depositoDolarPy:
            #depositoDolarPyValorTotal = (
            #    depositoDolarPyValorTotal + depositoDolarPyValor.saldoInicial
            #)

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

        context["cartaoCreditoValorTotal"] = cartaoCreditoValorTotal
        context["especieValorTotal"] = especieValorTotal
        context["depositoRealValorTotal"] = depositoRealValorTotal
        context["depositoDolarValorTotal"] = depositoDolarValorTotal
        context["depositoDolarPyValorTotal"] = depositoDolarPyValorTotal

        contasDetalhadasTemplate = []
        contaOrigem = []
        contaDestino = []
        for conta in contasDetalhadas:
            #saldoConta = conta.saldoInicial
            saldoConta = 0
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

        context["contasDetalhadas"] = contasDetalhadasTemplate
        context["contaOrigem"] = contaOrigem
        context["contaDestino"] = contaDestino

        # popular movimentações

        movimentacaoConta = MovimentacaoConta.objects.all()

        movimentacaoContasTemplate = []
        for conta in movimentacaoConta:
            # Se for uma movimentação de compra ou venda não listar
            try:
                contaCredito = Conta.objects.get(id=conta.contaCredito)
            except:
                continue
            try:
                contaDebito = Conta.objects.get(id=conta.contaDebito)
            except:
                continue

            movimentacaoContasTemplate.append(
                {
                    "data": conta.criados,
                    "contaOrigem": contaDebito.nomeConta,
                    "contaDestino": contaCredito.nomeConta,
                    "valorContaOrigem": conta.valorDebito,
                    "valorContaDestino": conta.valorCredito,
                    "idMovimento": conta.id,
                }
            )

        context["movimentacaoContas"] = movimentacaoContasTemplate

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
                context["mensagem"] = "Conta Apagada"

        # Popular template
        context["cartaoCreditoValorTotal"] = self.valores_cartao_credito
        context["especieValorTotal"] = self.valores_especie
        context["depositoRealValorTotal"] = self.valores_conta_real
        context["depositoDolarValorTotal"] = self.valores_dolar
        context["depositoDolarPyValorTotal"] = self.valores_dolar_paraguai

        # Popular template com dados de conta
        contas = self.contas_origem_e_detalhadas()
        context["contasDetalhadas"] = contas["contasDetalhadasTemplate"]
        context["contaOrigem"] = contas["contaOrigem"]
        # popular movimentações
        context["movimentacaoContas"] = self.movimentacoes_contas

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
        )
        dataform.save()
        context["mensagem"] = "Aporte Efetuado"

        # Popular template
        context["especieValorTotal"] = self.valores_especie
        context["depositoRealValorTotal"] = self.valores_conta_real
        context["depositoDolarValorTotal"] = self.valores_dolar
        context["depositoDolarPyValorTotal"] = self.valores_dolar_paraguai
        context["cartaoCreditoValorTotal"] = self.valores_cartao_credito

        # Popular template com dados de conta
        contas = self.contas_origem_e_detalhadas()
        context["contasDetalhadas"] = contas["contasDetalhadasTemplate"]
        context["contaOrigem"] = contas["contaOrigem"]

        # popular movimentações
        context["movimentacaoContas"] = self.movimentacoes_contas

        return super(TemplateView, self).render_to_response(context)

    def valores_cartao_credito(self):
        cartaoCredito = Conta.objects.filter(categoria_id=1)
        cartaoCreditoValorTotal = 0
        for cartaoCreditoValor in cartaoCredito:
            cartaoCreditoValorTotal = (
                cartaoCreditoValorTotal + cartaoCreditoValor.saldoInicial
            )
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
        especie = Conta.objects.filter(categoria_id=3)
        especieValorTotal = 0
        for especieValor in especie:
            especieValorTotal = especieValorTotal + especieValor.saldoInicial
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
            depositoRealValorTotal = (
                depositoRealValorTotal + depositoRealValor.saldoInicial
            )

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
            depositoDolarValorTotal = (
                depositoDolarValorTotal + depositoDolarValor.saldoInicial
            )

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

        return movimentacaoContasTemplate

    def contas_origem_e_detalhadas(self):
        contasDetalhadas = Conta.objects.all()
        contasDetalhadasTemplate = []
        contaOrigem = []
        contaDestino = []
        for conta in contasDetalhadas:
            saldoConta = conta.saldoInicial
            entradas = MovimentacaoConta.objects.filter(contaCredito=conta.id)

            for entrada in entradas:
                saldoConta = saldoConta + entrada.valorCredito

            saidas = MovimentacaoConta.objects.filter(contaDebito=conta.id)

            for saida in saidas:
                saldoConta = saldoConta - saida.valorDebito

            if conta.categoria_id <= 3 and conta.categoria_id >= 1:
                moeda = "R$"
            else:
                moeda = "US$"

            contaOrigem.append({"id": conta.id, "nomeConta": conta.nomeConta})

            contasDetalhadasTemplate.append(
                {"nomeConta": conta.nomeConta, "saldo": saldoConta, "moeda": moeda}
            )

        return {"contaOrigem" : contaOrigem, "contasDetalhadasTemplate": contasDetalhadasTemplate}
