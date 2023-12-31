from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import Compra, LocalizacaoCompra, Fornecedor, Deslocamento
from Produtos.models import Produto, CategoriaProduto
from Contas.models import Conta, MovimentacaoConta
from datetime import date, datetime
import re
import logging

class FazerComprasView(TemplateView):
    template_name = 'fazercompras.html'

    def get_context_data(self, **kwargs):
        context = super(FazerComprasView, self).get_context_data(**kwargs)
        context['editarCompra'] = 0
        context['dolarMedio'] = self.dolarMedio
        if self.request.GET.__contains__("idCompra"):
            compras = Compra.objects.filter(identificadorCompra=self.request.GET["idCompra"], ativo=True)
            listarProdutosTemplate = []
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
                context['dolarMedio'] = compra.valorDolarMedio

        context['compras'] = Compra.objects.all()
        context['mensagem'] = ''
        # Popular template
        context['fornecedores'] = Fornecedor.objects.all()
        context['produtos'] = Produto.objects.all().order_by('NomeProduto')
        context['localizacaoCompra'] = LocalizacaoCompra.objects.all()
        context['contasDetalhadas'] = self.saldoConta
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
        #Conta de saída do dinheiro
        contaOrigem = self.request.POST.getlist('contaOrigem')
        #Se a função for "Editar Compra" o valor será estornado para a conta de origem original da compra
        contaOrigemOriginal = self.request.POST.getlist('idConta')
        frete = self.request.POST.getlist('frete')
        localizacaoCompra = self.request.POST.getlist('localizacaoCompra')
        identificadorCompra = self.request.POST.getlist('identificadorCompra')
        cotacaoDolar = self.request.POST.getlist('dolarMedio')
        if frete[0] == "":
            frete[0] = 0
        else:
            frete = self.request.POST.getlist('frete')
        descricao = self.request.POST.getlist('descricao')

        dataModificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', dataCompra[0])
        contador = 0
        valorCompra = 0
        valorEstorno = 0

        # Desabilitando registro de Compra Salva caso função seja editar
        if identificadorCompra[0] != "":
            logging.warning(identificadorCompra[0])
            compraDesabilitada = Compra.objects.filter(identificadorCompra=identificadorCompra[0],ativo=True)
            #Devolvendo o dinheiro da Compra para a conta especifica
            for compra in compraDesabilitada:
                valorEstorno = valorEstorno + compra.quantidadeProduto*compra.precoProduto
            valorEstorno = valorEstorno + compra.frete
            proximaCompra = identificadorCompra[0]
            formMovimentacao = MovimentacaoConta(
                criados=str(dataModificada),
                contaCredito_id=contaOrigemOriginal[0],
                valorCredito=valorEstorno,
                identificadorCompra=str(proximaCompra),
                descricao=descricao,
            )
            formMovimentacao.save()
            #Atualizando o estoque
            logging.warning("Removendo")
            for produto in produtos:
                atualizarEstoque = Produto.objects.get(id=produto)
                quantidadeOriginalEstoque = Compra.objects.get(identificadorCompra=identificadorCompra[0],produto_id=produto,ativo=True)
                atualizarEstoque.estoque = atualizarEstoque.estoque - quantidadeOriginalEstoque.quantidadeProduto
                atualizarEstoque.save()
                contador = contador + 1
            Compra.objects.filter(identificadorCompra=identificadorCompra[0]).update(ativo=False)


        # Salvando Compra
        contador = 0
        cotacaoDolar = cotacaoDolar[0].replace(',','.')
        for produto in produtos:
            if precos[contador] != "" and quantidades[contador] != "":
                formCompra = Compra(
                    criados=str(dataModificada),
                    quantidadeProduto=quantidades[contador],
                    precoProduto=precos[contador],
                    identificadorCompra=str(proximaCompra),
                    fornecedor_id=fornecedor[0],
                    produto_id=produto,
#                    frete=frete[0],
                    descricao=descricao,
                    idLocalizacao_id=localizacaoCompra[0],
                    conta_id=contaOrigem[0],
                    valorDolarMedio=float(cotacaoDolar)
                )
                valorCompra = valorCompra + float(precos[contador]) * float(quantidades[contador])
                formCompra.save()
                #Atualizando o estoque
                logging.warning("Adicionando")
                atualizarEstoque = Produto.objects.get(id=produto)
                atualizarEstoque.estoque = atualizarEstoque.estoque + int(float(quantidades[contador]))
                atualizarEstoque.save()

                contador = contador + 1
        valorCompra = valorCompra + float(frete[0])

        tipoConta = Conta.objects.get(id=contaOrigem[0])
        identificadorDolar = False
        if tipoConta.categoria_id == 4 or tipoConta.categoria_id == 5:
            identificadorDolar = True
        # Debitando da conta
        formMovimentacao = MovimentacaoConta(
            criados=str(dataModificada),
            contaDebito=contaOrigem[0],
            valorDebito=valorCompra,
            identificadorCompra=str(proximaCompra),
            descricao=descricao,
            cotacaoDolar=float(cotacaoDolar),
            identificadorDolar=identificadorDolar,
        )
        formMovimentacao.save()

        context['mensagem'] = 'Compra Salva'

        # Popular template
        context['fornecedores'] = Fornecedor.objects.all()
        context['produtos'] = Produto.objects.all()
        context['localizacaoCompra'] = LocalizacaoCompra.objects.all()
        context['contasDetalhadas'] = self.saldoConta
        context['dolarMedio'] = self.dolarMedio
        return super(TemplateView, self).render_to_response(context)
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

    def saldoConta(self):
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
                    logging.warning(apagar.produto_id)
                    atualizarEstoque = Produto.objects.get(id=apagarcompra.produto_id)
                    atualizarEstoque.estoque = atualizarEstoque.estoque - apagarcompra.quantidadeProduto
                    atualizarEstoque.save()
                    apagar.delete()
                apagarmovimentacao = MovimentacaoConta.objects.filter(identificadorCompra=self.request.GET["idCompra"])
                apagarmovimentacao.delete()

        compras = Compra.objects.order_by('identificadorCompra').filter(ativo=True)

        listarComprasTemplate = []
        identificadorCompra = 0
        for compra in compras:
            if identificadorCompra != compra.identificadorCompra:
                compraIdentificada = Compra.objects.filter(identificadorCompra=compra.identificadorCompra, ativo=True)
                valorCompraTotal = 0
                frete = 0
                for compra in compraIdentificada:
                    frete = compra.frete
                    valorCompraTotal = valorCompraTotal + compra.quantidadeProduto * compra.precoProduto
                valorCompraTotal = valorCompraTotal + frete
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

class LocalizacaoCompraView(TemplateView):
    template_name = 'localizacaocompra.html'
    def get_context_data(self, **kwargs):
        context = super(LocalizacaoCompraView, self).get_context_data(**kwargs)
        logging.warning("Localizacao")
        localizacao_compra = Deslocamento.objects.filter(identificadorCompra = self.request.GET["idCompra"]).order_by('-id')
        logging.warning("Try " + self.request.GET["idCompra"])
        compra_deslocada = 0
        for localizacao in localizacao_compra:
            logging.warning("Localizacao Origem " + str(localizacao.destino))
            origem = localizacao.destino
            compra_deslocada = 1
            break
        if compra_deslocada == 0:
            logging.warning("Except")
            localizacao_compra = Compra.objects.filter(identificadorCompra = self.request.GET["idCompra"]).order_by('-id')
            for localizacao in localizacao_compra:
                origem = localizacao.idLocalizacao_id
                break
        context['origem_localizacao'] = origem
        context['localizacao_compra'] = LocalizacaoCompra.objects.all()
        context['contas_detalhadas'] = self.saldo_conta
        context['id_compra'] = self.request.GET["idCompra"]
        return(context)
    def post(self, request, *args, **kwargs):
        context = super(LocalizacaoCompraView, self).get_context_data(**kwargs)
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        logging.warning("Identificador Compra")
        logging.warning(self.request.POST.get('id_compra'))
        logging.warning(self.request.POST.get('origem'))
        logging.warning(self.request.POST.get('destino'))
        formDeslocamento = Deslocamento(
            criados=hoje,
            origem=self.request.POST.get('origem'),
            destino=self.request.POST.get('destino'),
            frete=self.request.POST.get('valor_frete'),
            identificadorCompra=self.request.POST.get('id_compra'),
        )
        formDeslocamento.save()
        # Debitando frete da conta
        conta_em_dolar = 0
        cotacao_dolar = 0
        conta_debito = Conta.objects.get(id=self.request.POST.get('conta'))
        if conta_debito.categoria_id > 3:
            conta_em_dolar = 1
            cotacao_dolar = self.dolarMedio()

        formMovimentacao = MovimentacaoConta(
            criados=hoje,
            contaDebito=self.request.POST.get('conta'),
            valorDebito=self.request.POST.get('valor_frete'),
            identificadorCompra=self.request.POST.get('id_compra'),
            descricao="Frete",
            cotacaoDolar=cotacao_dolar,
            identificadorDolar=conta_em_dolar,
        )
        formMovimentacao.save()
        return HttpResponseRedirect('/listarcompras/', context)

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
class AdicionarLocalizacao(TemplateView):
    template_name = 'adicionarlocalizacao.html'
    def get_context_data(self, **kwargs):
        context = super(AdicionarLocalizacao, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        context = super(AdicionarLocalizacao, self).get_context_data(**kwargs)