from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import Compra, LocalizacaoCompra
from core.models import Fornecedor, Produto, CategoriaProduto, Conta, MovimentacaoConta
from datetime import date, datetime
import re
import logging

class FazerComprasView(TemplateView):
    template_name = 'fazercompras.html'

    def get_context_data(self, **kwargs):
        context = super(FazerComprasView, self).get_context_data(**kwargs)
        context['editarCompra'] = 0
        if self.request.GET.__contains__("idCompra"):
            compras = Compra.objects.filter(identificadorCompra=self.request.GET["idCompra"], ativo=True)
            listarProdutosTemplate = []
            identificadorCompra = 0
            valorCompraTotal = 0
            context['editarCompra'] = 1

            for compra in compras:
                listarProdutosTemplate.append(
                    {
                        'idProduto': compra.produto_id,
                        'quantidadeProduto': compra.quantidadeProduto,
                        'precoProduto': compra.precoProduto,
                    }
                )
                context['frete'] = compra.frete
                context['idLocalizacao'] = compra.idLocalizacao_id
                context['dataCompra'] = compra.criados.strftime('%d-%m-%Y')
                context['idFornecedor'] = compra.fornecedor_id
                context['identificadorCompra'] = compra.identificadorCompra
                context['idConta'] = compra.conta_id
                context['compra_identificada'] = listarProdutosTemplate

        context['compras'] = Compra.objects.all()
        context['mensagem'] = ''
        # Popular template
        context['fornecedores'] = Fornecedor.objects.all()
        context['produtos'] = Produto.objects.all()
        context['localizacaoCompra'] = LocalizacaoCompra.objects.all()

        # Buscar saldo em contas
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

            if conta.categoria_id <= 3 and conta.categoria_id >= 1:
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

        fornecedor = self.request.POST.getlist('fornecedor')
        dataCompra = self.request.POST.getlist('dataCompra')
        produtos = self.request.POST.getlist('produto')
        quantidades = self.request.POST.getlist('qtde')
        precos = self.request.POST.getlist('preco')
        contaOrigem = self.request.POST.getlist('contaOrigem')
        frete = self.request.POST.getlist('frete')
        localizacaoCompra = self.request.POST.getlist('localizacaoCompra')
        identificadorCompra = self.request.POST.getlist('identificadorCompra')

        if frete[0] == "":
            frete[0] = 0
        else:
            frete = self.request.POST.getlist('frete')
        descricao = self.request.POST.getlist('descricao')

        dataModificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', dataCompra[0])
        contador = 0
        valorCompra = 0
        valorEstorno = 0
        logging.warning("1")
        # Desabilitando registro de Compra Salva caso função seja editar
        if identificadorCompra[0] != "":
            logging.warning(identificadorCompra[0])
            compraDesabilitada = Compra.objects.filter(identificadorCompra=identificadorCompra[0],ativo=True)
            #Devolvendo o dinheiro da Compra para a conta especifica
            for compra in compraDesabilitada:
                valorEstorno = valorEstorno + compra.quantidadeProduto*compra.precoProduto
            valorEstorno = valorEstorno + compra.frete
            formMovimentacao = MovimentacaoConta(
                criados=str(dataModificada),
                contaCredito_id=contaOrigem[0],
                valorCredito=valorEstorno,
                identificadorCompra=str(proximaCompra),
                descricao=descricao,
            )
            formMovimentacao.save()
            #Atualizando o estoque
            logging.warning("Removendo")
            for produto in produtos:
                atualizarEstoque = Produto.objects.get(id=produto)
                atualizarEstoque.estoque = atualizarEstoque.estoque - int(float(quantidades[contador]))
                atualizarEstoque.save()
                contador = contador + 1
                logging.warning(atualizarEstoque.NomeProduto)
                logging.warning(atualizarEstoque.estoque)
            Compra.objects.filter(identificadorCompra=identificadorCompra[0]).update(ativo=False)
            proximaCompra = identificadorCompra[0]

        # Salvando Compra
        contador = 0
        for produto in produtos:
            if precos[contador] != "" and quantidades[contador] != "":
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
                    conta_id=contaOrigem[0]
                )
                valorCompra = valorCompra + float(precos[contador]) * float(quantidades[contador])
                formCompra.save()
                #Atualizando o estoque
                logging.warning("Adicionando")
                atualizarEstoque = Produto.objects.get(id=produto)
                atualizarEstoque.estoque =  atualizarEstoque.estoque + int(float(quantidades[contador]))
                atualizarEstoque.save()
                logging.warning(atualizarEstoque.NomeProduto)
                logging.warning(atualizarEstoque.estoque)
                contador = contador + 1
        valorCompra = valorCompra + float(frete[0])

        # Debitando da conta
        formMovimentacao = MovimentacaoConta(
            criados=str(dataModificada),
            contaDebito=contaOrigem[0],
            valorDebito=valorCompra,
            identificadorCompra=str(proximaCompra),
            descricao=descricao,
        )
        formMovimentacao.save()

        context['mensagem'] = 'Compra Salva'

        # Popular template
        context['fornecedores'] = Fornecedor.objects.all()
        context['produtos'] = Produto.objects.all()
        context['localizacaoCompra'] = LocalizacaoCompra.objects.all()

        # Buscar saldo em contas
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

            if conta.categoria_id <= 3 and conta.categoria_id >= 1:
                moeda = 'R$'
            else:
                moeda = 'US$'

            contasDetalhadasTemplate.append(
                {'nomeConta': conta.nomeConta, 'saldo': saldoConta, 'moeda': moeda, 'id': conta.id})

        context['contasDetalhadas'] = contasDetalhadasTemplate

        return super(TemplateView, self).render_to_response(context)


class ListarComprasView(TemplateView):
    template_name = 'listarcompras.html'

    def get_context_data(self, **kwargs):
        context = super(ListarComprasView, self).get_context_data(**kwargs)

        context['mensagem'] = ''
        if self.request.GET.__contains__("idCompra"):
            if self.request.GET["funcao"] == "apagar":
                apagarcompras = Compra.objects.filter(identificadorCompra=self.request.GET["idCompra"])
                for apagarcompra in apagarcompras:
                    apagar = Compra(id=apagarcompra.id)
                    apagar.delete()

        compras = Compra.objects.order_by('identificadorCompra').filter(ativo=True)

        listarComprasTemplate = []
        identificadorCompra = 0
        for compra in compras:
            if identificadorCompra != compra.identificadorCompra:
                compraIdentificada = Compra.objects.filter(identificadorCompra=compra.identificadorCompra, ativo=True)
                valorCompraTotal = 0
                for compra in compraIdentificada:
                    valorCompraTotal = valorCompraTotal + compra.quantidadeProduto * compra.precoProduto
                listarComprasTemplate.append(
                    {
                        'idCompra': compra.identificadorCompra,
                        'fornecedor': compra.fornecedor,
                        'dataCompra': compra.criados,
                        'valorCompra': valorCompraTotal,
                        'localizacaoCompra': compra.idLocalizacao.localizacaoCompra,
                    }
                )
                valorCompraTotal = 0
                identificadorCompra = compra.identificadorCompra
        context['listarCompras'] = listarComprasTemplate

        # from django.db.models import F
        # lista_identificadores = compras.distinct().values_list('identificadorCompra', flat=True)
        # for identificador in lista_identificadores:
        #     compra = Compra.objects.filter(
        #         identificadorCompra=identificador, ativo=True).annotate(
        #         valorCompraTotal=Sum(F('quantidadeProduto') * F('precoProduto')
        #                              )
        #     )
        #     listarComprasTemplate.append(
        #         {
        #             'idCompra': compra.identificadorCompra,
        #             'fornecedor': compra.fornecedor,
        #             'dataCompra': compra.criados,
        #             'valorCompra': compra.valorCompraTotal,
        #             'localizacaoCompra': compra.idLocalizacao.localizacaoCompra,
        #         }
        #     )

        return (context)

