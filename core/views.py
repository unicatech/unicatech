from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import Produto, CategoriaProduto, Conta, CategoriaConta, MovimentacaoConta, Fornecedor, Compra, LocalizacaoCompra

import re

class IndexView(TemplateView):
    template_name = 'index.html'

class ProductListView(TemplateView):
    template_name = 'productlist.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['mensagem'] = ''
        if self.request.GET.__contains__("idProduto"):
            if self.request.GET["funcao"] == "apagar":
                apagarproduto = Produto(id=self.request.GET["idProduto"])
                apagarproduto.delete()
        if self.request.GET.__contains__("produtocadastrado"):
            context['mensagem'] = 'Produto Salvo'
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['produtos'] = Produto.objects.all()
        context['categoriaproduto'] = CategoriaProduto.objects.all()
        return context

class AddProductView(TemplateView):
    template_name = 'addproduct.html'

    def get_context_data(self, **kwargs):
        context = super(AddProductView, self).get_context_data(**kwargs)
        context['categoriaproduto'] = CategoriaProduto.objects.all()
        context['mensagem'] = ''
        return context

    def post(self, request, *args, **kwargs):
        dataform = Produto(
                           NomeProduto=self.request.POST.get('nomeproduto'),
                           categoria_id=self.request.POST.get('categoria'),
                           SKU=self.request.POST.get('SKU'),
                           estoque=self.request.POST.get('estoque')
                           )
        dataform.save()
        context = super(AddProductView, self).get_context_data(**kwargs)
        context['mensagem'] = 'Produto Salvo'
        context['categoriaproduto'] = CategoriaProduto.objects.all()
        return super(TemplateView, self).render_to_response(context)

class EditProductView(TemplateView):
    template_name = 'editproduct.html'

    def get_context_data(self, **kwargs):
        context = super(EditProductView, self).get_context_data(**kwargs)
        context['categoriaproduto'] = CategoriaProduto.objects.all()
        context['produtoselecionado'] = Produto.objects.get(id=self.request.GET["idProduto"])
        context['categoriaprodutoselecionado'] = CategoriaProduto.objects.get(categoria=context['produtoselecionado'].categoria)
        context['mensagem'] = ''
        return context

    def post(self, request, *args, **kwargs):
        dataform =Produto.objects.get(id=self.request.POST.get('idProduto'))
        dataform.NomeProduto = self.request.POST.get('nomeproduto')
        dataform.categoria_id = self.request.POST.get('categoria')
        dataform.SKU = self.request.POST.get('SKU')
        dataform.estoque = self.request.POST.get('estoque')
        dataform.save()
        context = super(EditProductView, self).get_context_data(**kwargs)
        context['produtos'] = Produto.objects.all()
        context['categoriaproduto'] = CategoriaProduto.objects.all()
        return HttpResponseRedirect('/productlist/?produtocadastrado=1')

class CriarContaView(TemplateView):
    template_name = 'addaccount.html'

    def get_context_data(self, **kwargs):
        context = super(CriarContaView, self).get_context_data(**kwargs)
        context['categoria'] = CategoriaConta.objects.all()
        context['mensagem'] = ''
        return context

    def post(self, request, *args, **kwargs):
        dataform = Conta(
                         nomeConta=self.request.POST.get('nomeConta'),
                         categoria_id=self.request.POST.get('categoria'),
                         descricao=self.request.POST.get('descricao'),
                         saldoInicial=self.request.POST.get('saldoinicial'),
                         taxas=self.request.POST.get('taxas')
                        )
        dataform.save()
        context = super(CriarContaView, self).get_context_data(**kwargs)
        context['mensagem'] = 'Conta Salva'
        context['categoria'] = CategoriaConta.objects.all()
        return super(TemplateView, self).render_to_response(context)

class ListarContaView(TemplateView):
    template_name = 'accountlist.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['mensagem'] = ''
        if self.request.GET.__contains__("idConta"):
            if self.request.GET["funcao"] == "apagar":
                apagarconta = Conta(id=self.request.GET["idConta"])
                apagarconta.delete()
        if self.request.GET.__contains__("contacadastrada"):
            context['mensagem'] = 'Conta Salva'
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ListarContaView, self).get_context_data(**kwargs)
        context['contas'] = Conta.objects.all()
        context['categoriaconta'] = CategoriaConta.objects.all()
        return context

class EditarContaView(TemplateView):
    template_name = 'editaccount.html'

    def get_context_data(self, **kwargs):
        context = super(EditarContaView, self).get_context_data(**kwargs)
        context['categoria'] = CategoriaConta.objects.all()
        context['contaselecionada'] = Conta.objects.get(id=self.request.GET["idConta"])
        context['contaselecionada'].taxas = str(float(context['contaselecionada'].taxas))
        context['contaselecionada'].saldoInicial = str(float(context['contaselecionada'].saldoInicial))
        context['categoriacontaselecionada'] = CategoriaConta.objects.get(categoria=context['contaselecionada'].categoria)
        context['mensagem'] = ''
        return context

    def post(self, request, *args, **kwargs):
        dataform = Conta.objects.get(id=self.request.POST.get('idConta'))
        dataform.nomeConta = self.request.POST.get('nomeConta')
        dataform.categoria_id = self.request.POST.get('categoria')
        dataform.taxas = self.request.POST.get('taxas')
        dataform.descricao = self.request.POST.get('descricao')
        dataform.saldoInicial = self.request.POST.get('saldoinicial')
        dataform.save()
        context = super(EditarContaView, self).get_context_data(**kwargs)
        context['conta'] = Conta.objects.all()
        context['categoriaconta'] = CategoriaConta.objects.all()
        return HttpResponseRedirect('/listarconta/?contacadastrada=1')

class ComprarDolarView(TemplateView):
    template_name = 'compradolar.html'

    def get_context_data(self, **kwargs):
        context = super(ComprarDolarView, self).get_context_data(**kwargs)
        context['mensagem'] = ""
        if self.request.GET.__contains__("idMovimento"):
            if self.request.GET["funcao"] == "apagar":
                apagarproduto = MovimentacaoConta(id=self.request.GET["idMovimento"])
                apagarproduto.delete()
                context['mensagem'] = "Conta Apagada"

        # Popular template com dados de conta
        cartaoCredito = Conta.objects.filter(categoria_id=1)
        especie = Conta.objects.filter(categoria_id=3)
        depositoReal = Conta.objects.filter(categoria_id=2)
        depositoDolar = Conta.objects.filter(categoria_id=4)
        depositoDolarPy = Conta.objects.filter(categoria_id=5)
        contasDetalhadas = Conta.objects.all()

        cartaoCreditoValorTotal = 0
        for cartaoCreditoValor in cartaoCredito:
            cartaoCreditoValorTotal = cartaoCreditoValorTotal + cartaoCreditoValor.saldoInicial

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(contaCredito=cartaoCreditoValor.id)
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal + conta.valorCredito

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(contaDebito=cartaoCreditoValor.id)
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal - conta.valorDebito

        especieValorTotal = 0
        for especieValor in especie:
            especieValorTotal = especieValorTotal + especieValor.saldoInicial

            especieMovimento = MovimentacaoConta.objects.filter(contaCredito=especieValor.id)
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal + conta.valorCredito

            especieMovimento = MovimentacaoConta.objects.filter(contaDebito=especieValor.id)
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal - conta.valorDebito

        depositoRealValorTotal = 0
        for depositoRealValor in depositoReal:
            depositoRealValorTotal = depositoRealValorTotal + depositoRealValor.saldoInicial

            depositoRealMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoRealValor.id)
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal + conta.valorCredito

            depositoRealMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoRealValor.id)
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal - conta.valorDebito

        depositoDolarValorTotal = 0
        for depositoDolarValor in depositoDolar:
            depositoDolarValorTotal = depositoDolarValorTotal + depositoDolarValor.saldoInicial

            depositoDolarMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoDolarValor.id)
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal + conta.valorCredito

            depositoDolarMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoDolarValor.id)
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal - conta.valorDebito

        depositoDolarPyValorTotal = 0
        for depositoDolarPyValor in depositoDolarPy:
            depositoDolarPyValorTotal = depositoDolarPyValorTotal + depositoDolarPyValor.saldoInicial

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoDolarPyValor.id)
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = depositoDolarPyValorTotal + conta.valorCredito

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoDolarPyValor.id)
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = depositoDolarPyValorTotal - conta.valorDebito

        context['cartaoCreditoValorTotal'] = cartaoCreditoValorTotal
        context['especieValorTotal'] = especieValorTotal
        context['depositoRealValorTotal'] = depositoRealValorTotal
        context['depositoDolarValorTotal'] = depositoDolarValorTotal
        context['depositoDolarPyValorTotal'] = depositoDolarPyValorTotal

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

            if conta.categoria_id <= 3:
                moeda = 'R$'
                contaOrigem.append({'id': conta.id, 'nomeConta': conta.nomeConta})
            else:
                moeda = 'US$'
                contaDestino.append({'id': conta.id, 'nomeConta': conta.nomeConta})

            contasDetalhadasTemplate.append({'nomeConta': conta.nomeConta, 'saldo': saldoConta, 'moeda': moeda})

        context['contasDetalhadas'] = contasDetalhadasTemplate
        context['contaOrigem'] = contaOrigem
        context['contaDestino'] = contaDestino

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
                {'data': conta.criados,
                 'contaOrigem': contaDebito.nomeConta,
                 'contaDestino': contaCredito.nomeConta,
                 'valorContaOrigem': conta.valorDebito,
                 'valorContaDestino': conta.valorCredito,
                 'idMovimento': conta.id}
            )

        context['movimentacaoContas'] = movimentacaoContasTemplate

        return context

    def post(self, request, *args, **kwargs):
        context = super(ComprarDolarView, self).get_context_data(**kwargs)
        dataform = MovimentacaoConta(contaCredito=self.request.POST.get('contaDestino'), contaDebito=self.request.POST.get('contaOrigem'), valorCredito=float(self.request.POST.get('valorReal'))/float(self.request.POST.get('cotacao')),valorDebito=self.request.POST.get('valorReal'))
        dataform.save()
        context['mensagem'] = 'Compra Efetuada'
        # Popular template com dados de conta
        cartaoCredito = Conta.objects.filter(categoria_id=1)
        especie = Conta.objects.filter(categoria_id=3)
        depositoReal = Conta.objects.filter(categoria_id=2)
        depositoDolar = Conta.objects.filter(categoria_id=4)
        depositoDolarPy = Conta.objects.filter(categoria_id=5)
        contasDetalhadas = Conta.objects.all()

        cartaoCreditoValorTotal = 0
        for cartaoCreditoValor in cartaoCredito:
            cartaoCreditoValorTotal = cartaoCreditoValorTotal + cartaoCreditoValor.saldoInicial

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(contaCredito=cartaoCreditoValor.id)
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal + conta.valorCredito

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(contaDebito=cartaoCreditoValor.id)
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal - conta.valorDebito

        especieValorTotal = 0
        for especieValor in especie:
            especieValorTotal = especieValorTotal + especieValor.saldoInicial

            especieMovimento = MovimentacaoConta.objects.filter(contaCredito=especieValor.id)
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal + conta.valorCredito

            especieMovimento = MovimentacaoConta.objects.filter(contaDebito=especieValor.id)
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal - conta.valorDebito

        depositoRealValorTotal = 0
        for depositoRealValor in depositoReal:
            depositoRealValorTotal = depositoRealValorTotal + depositoRealValor.saldoInicial

            depositoRealMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoRealValor.id)
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal + conta.valorCredito

            depositoRealMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoRealValor.id)
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal - conta.valorDebito

        depositoDolarValorTotal = 0
        for depositoDolarValor in depositoDolar:
            depositoDolarValorTotal = depositoDolarValorTotal + depositoDolarValor.saldoInicial

            depositoDolarMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoDolarValor.id)
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal + conta.valorCredito

            depositoDolarMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoDolarValor.id)
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal - conta.valorDebito

        depositoDolarPyValorTotal = 0
        for depositoDolarPyValor in depositoDolarPy:
            depositoDolarPyValorTotal = depositoDolarPyValorTotal + depositoDolarPyValor.saldoInicial

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoDolarPyValor.id)
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = depositoDolarPyValorTotal + conta.valorCredito

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoDolarPyValor.id)
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = depositoDolarPyValorTotal - conta.valorDebito

        context['cartaoCreditoValorTotal'] = cartaoCreditoValorTotal
        context['especieValorTotal'] = especieValorTotal
        context['depositoRealValorTotal'] = depositoRealValorTotal
        context['depositoDolarValorTotal'] = depositoDolarValorTotal
        context['depositoDolarPyValorTotal'] = depositoDolarPyValorTotal

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

            if conta.categoria_id <= 3:
                moeda = 'R$'
                contaOrigem.append({'id': conta.id, 'nomeConta': conta.nomeConta})
            else:
                moeda = 'US$'
                contaDestino.append({'id': conta.id, 'nomeConta': conta.nomeConta})

            contasDetalhadasTemplate.append({'nomeConta': conta.nomeConta, 'saldo': saldoConta, 'moeda': moeda})

        context['contasDetalhadas'] = contasDetalhadasTemplate
        context['contaOrigem'] = contaOrigem
        context['contaDestino'] = contaDestino

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
                {'data': conta.criados,
                 'contaOrigem': contaDebito.nomeConta,
                 'contaDestino': contaCredito.nomeConta,
                 'valorContaOrigem': conta.valorDebito,
                 'valorContaDestino': conta.valorCredito,
                 'idMovimento': conta.id}
            )

        context['movimentacaoContas'] = movimentacaoContasTemplate

        return super(TemplateView, self).render_to_response(context)

class AdicionarFundosView(TemplateView):
    template_name = 'adicionarfundos.html'

    def get_context_data(self, **kwargs):
        context = super(AdicionarFundosView, self).get_context_data(**kwargs)
        context['mensagem'] = ""
        if self.request.GET.__contains__("idMovimento"):
            if self.request.GET["funcao"] == "apagar":
                apagarproduto = MovimentacaoConta(id=self.request.GET["idMovimento"])
                apagarproduto.delete()
                context['mensagem'] = "Conta Apagada"

        # Popular template com dados de conta
        cartaoCredito = Conta.objects.filter(categoria_id=1)
        especie = Conta.objects.filter(categoria_id=3)
        depositoReal = Conta.objects.filter(categoria_id=2)
        depositoDolar = Conta.objects.filter(categoria_id=4)
        depositoDolarPy = Conta.objects.filter(categoria_id=5)
        contasDetalhadas = Conta.objects.all()

        cartaoCreditoValorTotal = 0
        for cartaoCreditoValor in cartaoCredito:
            cartaoCreditoValorTotal = cartaoCreditoValorTotal + cartaoCreditoValor.saldoInicial

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(contaCredito=cartaoCreditoValor.id)
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal + conta.valorCredito

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(contaDebito=cartaoCreditoValor.id)
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal - conta.valorDebito

        especieValorTotal = 0
        for especieValor in especie:
            especieValorTotal = especieValorTotal + especieValor.saldoInicial

            especieMovimento = MovimentacaoConta.objects.filter(contaCredito=especieValor.id)
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal + conta.valorCredito

            especieMovimento = MovimentacaoConta.objects.filter(contaDebito=especieValor.id)
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal - conta.valorDebito

        depositoRealValorTotal = 0
        for depositoRealValor in depositoReal:
            depositoRealValorTotal = depositoRealValorTotal + depositoRealValor.saldoInicial

            depositoRealMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoRealValor.id)
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal + conta.valorCredito

            depositoRealMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoRealValor.id)
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal - conta.valorDebito

        depositoDolarValorTotal = 0
        for depositoDolarValor in depositoDolar:
            depositoDolarValorTotal = depositoDolarValorTotal + depositoDolarValor.saldoInicial

            depositoDolarMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoDolarValor.id)
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal + conta.valorCredito

            depositoDolarMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoDolarValor.id)
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal - conta.valorDebito

        depositoDolarPyValorTotal = 0
        for depositoDolarPyValor in depositoDolarPy:
            depositoDolarPyValorTotal = depositoDolarPyValorTotal + depositoDolarPyValor.saldoInicial

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoDolarPyValor.id)
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = depositoDolarPyValorTotal + conta.valorCredito

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoDolarPyValor.id)
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = depositoDolarPyValorTotal - conta.valorDebito

        context['cartaoCreditoValorTotal'] = cartaoCreditoValorTotal
        context['especieValorTotal'] = especieValorTotal
        context['depositoRealValorTotal'] = depositoRealValorTotal
        context['depositoDolarValorTotal'] = depositoDolarValorTotal
        context['depositoDolarPyValorTotal'] = depositoDolarPyValorTotal

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

            if conta.categoria_id <= 3:
                moeda = 'R$'
            else:
                moeda = 'US$'

            contaOrigem.append({'id': conta.id, 'nomeConta': conta.nomeConta})

            contasDetalhadasTemplate.append({'nomeConta': conta.nomeConta, 'saldo': saldoConta, 'moeda': moeda})

        context['contasDetalhadas'] = contasDetalhadasTemplate
        context['contaOrigem'] = contaOrigem
        context['contaDestino'] = contaDestino

        # popular movimentações

        movimentacaoConta = MovimentacaoConta.objects.all()[:10]

        movimentacaoContasTemplate = []
        for conta in movimentacaoConta:

            # Se for uma movimentação de compra ou venda ou movimentação entre contas não listar
            try:
                contaDebito = Conta.objects.get(id=conta.contaDebito)
            except:
                if conta.identificadorCompra == 0 and conta.identificadorVenda == 0:
                    contaCredito = Conta.objects.get(id=conta.contaCredito)
                    print(conta.contaCredito)
                    movimentacaoContasTemplate.append(
                        {'data': conta.criados,
                         'contaOrigem': contaCredito.nomeConta,
                         'valorContaOrigem': conta.valorCredito,
                         'idMovimento': conta.id}
                    )

        context['movimentacaoContas'] = movimentacaoContasTemplate

        return context

    def post(self, request, *args, **kwargs):
        context = super(AdicionarFundosView, self).get_context_data(**kwargs)
        dataform = MovimentacaoConta(contaCredito=self.request.POST.get('contaOrigem'), contaDebito="0", valorCredito=self.request.POST.get('valorReal'),valorDebito="0")
        dataform.save()
        context['mensagem'] = 'Aporte Efetuado'
        # Popular template com dados de conta
        cartaoCredito = Conta.objects.filter(categoria_id=1)
        especie = Conta.objects.filter(categoria_id=3)
        depositoReal = Conta.objects.filter(categoria_id=2)
        depositoDolar = Conta.objects.filter(categoria_id=4)
        depositoDolarPy = Conta.objects.filter(categoria_id=5)
        contasDetalhadas = Conta.objects.all()

        cartaoCreditoValorTotal = 0
        for cartaoCreditoValor in cartaoCredito:
            cartaoCreditoValorTotal = cartaoCreditoValorTotal + cartaoCreditoValor.saldoInicial

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(contaCredito=cartaoCreditoValor.id)
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal + conta.valorCredito

            cartaoCreditoMovimento = MovimentacaoConta.objects.filter(contaDebito=cartaoCreditoValor.id)
            for conta in cartaoCreditoMovimento:
                cartaoCreditoValorTotal = cartaoCreditoValorTotal - conta.valorDebito

        especieValorTotal = 0
        for especieValor in especie:
            especieValorTotal = especieValorTotal + especieValor.saldoInicial

            especieMovimento = MovimentacaoConta.objects.filter(contaCredito=especieValor.id)
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal + conta.valorCredito

            especieMovimento = MovimentacaoConta.objects.filter(contaDebito=especieValor.id)
            for conta in especieMovimento:
                especieValorTotal = especieValorTotal - conta.valorDebito

        depositoRealValorTotal = 0
        for depositoRealValor in depositoReal:
            depositoRealValorTotal = depositoRealValorTotal + depositoRealValor.saldoInicial

            depositoRealMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoRealValor.id)
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal + conta.valorCredito

            depositoRealMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoRealValor.id)
            for conta in depositoRealMovimento:
                depositoRealValorTotal = depositoRealValorTotal - conta.valorDebito

        depositoDolarValorTotal = 0
        for depositoDolarValor in depositoDolar:
            depositoDolarValorTotal = depositoDolarValorTotal + depositoDolarValor.saldoInicial

            depositoDolarMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoDolarValor.id)
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal + conta.valorCredito

            depositoDolarMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoDolarValor.id)
            for conta in depositoDolarMovimento:
                depositoDolarValorTotal = depositoDolarValorTotal - conta.valorDebito

        depositoDolarPyValorTotal = 0
        for depositoDolarPyValor in depositoDolarPy:
            depositoDolarPyValorTotal = depositoDolarPyValorTotal + depositoDolarPyValor.saldoInicial

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(contaCredito=depositoDolarPyValor.id)
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = depositoDolarPyValorTotal + conta.valorCredito

            depositoDolarPyMovimento = MovimentacaoConta.objects.filter(contaDebito=depositoDolarPyValor.id)
            for conta in depositoDolarPyMovimento:
                depositoDolarPyValorTotal = depositoDolarPyValorTotal - conta.valorDebito

        context['cartaoCreditoValorTotal'] = cartaoCreditoValorTotal
        context['especieValorTotal'] = especieValorTotal
        context['depositoRealValorTotal'] = depositoRealValorTotal
        context['depositoDolarValorTotal'] = depositoDolarValorTotal
        context['depositoDolarPyValorTotal'] = depositoDolarPyValorTotal

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

            if conta.categoria_id <= 3:
                moeda = 'R$'
            else:
                moeda = 'US$'

            contaOrigem.append({'id': conta.id, 'nomeConta': conta.nomeConta})

            contasDetalhadasTemplate.append({'nomeConta': conta.nomeConta, 'saldo': saldoConta, 'moeda': moeda})

        context['contasDetalhadas'] = contasDetalhadasTemplate
        context['contaOrigem'] = contaOrigem
        context['contaDestino'] = contaDestino

        # popular movimentações
        movimentacaoConta = MovimentacaoConta.objects.all()[:10]
        movimentacaoContasTemplate = []
        for conta in movimentacaoConta:
            # Se for uma movimentação de compra ou venda ou movimentação entre contas não listar
            try:
                contaDebito = Conta.objects.get(id=conta.contaDebito)
            except:
                if conta.identificadorCompra == 0 and conta.identificadorVenda == 0:
                    contaCredito = Conta.objects.get(id=conta.contaCredito)
                    print(conta.contaCredito)
                    movimentacaoContasTemplate.append(
                        {'data': conta.criados,
                         'contaOrigem': contaCredito.nomeConta,
                         'valorContaOrigem': conta.valorCredito,
                         'idMovimento': conta.id}
                    )

        context['movimentacaoContas'] = movimentacaoContasTemplate

        return super(TemplateView, self).render_to_response(context)



class ListarComprasView(TemplateView):
    template_name = 'listarcompras.html'

    def get_context_data(self, **kwargs):
        context = super(ListarComprasView, self).get_context_data(**kwargs)
        compras = Compra.objects.order_by('identificadorCompra')

        listarComprasTemplate = []
        identificadorCompra = 0
        valorCompraTotal = 0
        for compra in compras:
            if identificadorCompra != compra.identificadorCompra:
                listarComprasTemplate.append(
                    {'idCompra': compra.identificadorCompra,
                     'fornecedor': compra.fornecedor,
                     'dataCompra': compra.criados,
                     'valorCompra': valorCompraTotal,
                     'localizacaoCompra': compra.idLocalizacao.localizacaoCompra,
                     }
                )
                identificadorCompra = compra.identificadorCompra
        context['listarCompras'] = listarComprasTemplate
        return(context)
class FazerComprasView(TemplateView):
    template_name = 'fazercompras.html'

    def get_context_data(self, **kwargs):
        context = super(FazerComprasView, self).get_context_data(**kwargs)
        context['compras'] = Compra.objects.all()
        context['mensagem'] = ''
        #Popular template
        context['fornecedores'] = Fornecedor.objects.all()
        context['produtos'] = Produto.objects.all()
        context['localizacaoCompra'] = LocalizacaoCompra.objects.all()

        #Buscar saldo em contas
        contasDetalhadas = Conta.objects.all()
        contasDetalhadasTemplate = []

        for conta in contasDetalhadas:
            saldoConta = conta.saldoInicial
            entradas = MovimentacaoConta.objects.filter(contaCredito=conta.id)

            for entrada in entradas:
                saldoConta = saldoConta + entrada.valorCredito

            saidas = MovimentacaoConta.objects.filter(contaDebito=conta.id)

            for saida in saidas:
                saldoConta = saldoConta - saida.valorDebito

            if conta.categoria_id <= 3:
                moeda = 'R$'
            else:
                moeda = 'US$'

            contasDetalhadasTemplate.append({'nomeConta' : conta.nomeConta, 'saldo' : saldoConta, 'moeda' : moeda, 'id' : conta.id})

        context['contasDetalhadas'] = contasDetalhadasTemplate
        return context

    def post(self, request, *args, **kwargs):
        context = super(FazerComprasView, self).get_context_data(**kwargs)

        try:
            ultimaCompra = Compra.objects.last()
            proximaCompra = ultimaCompra.identificadorCompra + 1
        except:
            proximaCompra = 1

        print(self.request.POST.get)
        fornecedor = self.request.POST.getlist('fornecedor')
        dataCompra = self.request.POST.getlist('dataCompra')
        produtos = self.request.POST.getlist('produto')
        quantidades = self.request.POST.getlist('qtde')
        precos = self.request.POST.getlist('preco')
        contaOrigem = self.request.POST.getlist('contaOrigem')
        frete = self.request.POST.getlist('frete')
        localizacaoCompra = self.request.POST.getlist('localizacaoCompra')

        if frete[0] == "":
            frete[0] = 0
        else:
            frete = self.request.POST.getlist('frete')
        descricao = self.request.POST.getlist('descricao')

        dataModificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', dataCompra[0])

        contador = 0
        valorCompra = 0

        for produto in produtos:
            formCompra = Compra(
                             criados=str(dataModificada),
                             quantidadeProduto=quantidades[contador],
                             precoProduto=precos[contador],
                             identificadorCompra=str(proximaCompra),
                             fornecedor_id=fornecedor[0],
                             produto_id=produto,
                             frete=frete[0],
                             descricao=descricao,
                             idLocalizacao_id=localizacaoCompra[0],
                             )
            valorCompra = valorCompra + float(precos[contador])*float(quantidades[contador])
            formCompra.save()
            contador = contador + 1
        valorCompra = valorCompra + float(frete[0])

        formMovimentacao = MovimentacaoConta(
                             criados=str(dataModificada),
                             contaDebito=contaOrigem[0],
                             valorDebito=valorCompra,
                             identificadorCompra=str(proximaCompra),
                             descricao=descricao,
                             )
        formMovimentacao.save()

        context['mensagem'] = 'Compra Salva'

        #Popular template
        context['fornecedores'] = Fornecedor.objects.all()
        context['produtos'] = Produto.objects.all()
        context['localizacaoCompra'] = LocalizacaoCompra.objects.all()

        #Buscar saldo em contas
        contasDetalhadas = Conta.objects.all()
        contasDetalhadasTemplate = []

        for conta in contasDetalhadas:
            saldoConta = conta.saldoInicial
            entradas = MovimentacaoConta.objects.filter(contaCredito=conta.id)

            for entrada in entradas:
                saldoConta = saldoConta + entrada.valorCredito

            saidas = MovimentacaoConta.objects.filter(contaDebito=conta.id)

            for saida in saidas:
                saldoConta = saldoConta - saida.valorDebito

            if conta.categoria_id <= 3:
                moeda = 'R$'
            else:
                moeda = 'US$'

            contasDetalhadasTemplate.append({'nomeConta' : conta.nomeConta, 'saldo' : saldoConta, 'moeda' : moeda, 'id' : conta.id})

        context['contasDetalhadas'] = contasDetalhadasTemplate

        return super(TemplateView, self).render_to_response(context)

class EditarComprasView(TemplateView):
    template_name = 'editarcompras.html'
    def get_context_data(self, **kwargs):
        context = super(EditarComprasView, self).get_context_data(**kwargs)
        compras = Compra.objects.get(id=self.request.GET["idCompra"])

        listarComprasTemplate = []
        identificadorCompra = 0
        valorCompraTotal = 0
        for compra in compras:
            listarComprasTemplate.append(
                    {'idCompra': compra.identificadorCompra,
                     'fornecedor': compra.fornecedor_id.nomeFornecedor,
                     'dataCompra': compra.criados,
                     'idProduto': compra.produto_id,
                     'nomeProduto': compra.produto_id.NomeProduto,
                     'idLocalizacao': compra.localizacao_id,
                     'quantidadeProduto': compra.quantidadeProduto,
                     'precoProduto': compra.precoProduto,
                     'nomeLocalizacao': compra.localizacao_id.localizacaoCompra,
                     'localizacaoCompra': compra.idLocalizacao.localizacaoCompra,
                     }
            )
            #identificadorCompra = compra.identificadorCompra

        context['listarCompras'] = listarComprasTemplate
        return context

    def post(self, request, *args, **kwargs):
        dataform = Conta.objects.get(id=self.request.POST.get('idConta'))
        dataform.nomeConta = self.request.POST.get('nomeConta')
        dataform.categoria_id = self.request.POST.get('categoria')
        dataform.taxas = self.request.POST.get('taxas')
        dataform.descricao = self.request.POST.get('descricao')
        dataform.saldoInicial = self.request.POST.get('saldoinicial')
        dataform.save()
        context = super(EditarContaView, self).get_context_data(**kwargs)
        context['conta'] = Conta.objects.all()
        context['categoriaconta'] = CategoriaConta.objects.all()
        return HttpResponseRedirect('/listarconta/?contacadastrada=1')