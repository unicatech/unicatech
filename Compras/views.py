from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import Compra, LocalizacaoCompra, Fornecedor, Deslocamento
from Produtos.models import Produto, CategoriaProduto
from Contas.models import Conta, MovimentacaoConta
from Contas.views import MovimentacaoFinanceira
from datetime import date, datetime, timedelta
from django.utils import timezone
import re
import logging

class FazerComprasView(TemplateView):
    template_name = 'fazercompras.html'

    def get_context_data(self, **kwargs):
        context = super(FazerComprasView, self).get_context_data(**kwargs)
        context['editarCompra'] = 0
        context['dataCompra'] = datetime.now().strftime("%d-%m-%Y")
        financeiro = MovimentacaoFinanceira()
        context['dolarMedio'] = financeiro.dolarMedio
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
                #context['frete'] = compra.frete
                context['idLocalizacao'] = compra.idLocalizacao_id
                context['dataCompra'] = compra.criados.strftime('%d-%m-%Y')
                context['idFornecedor'] = compra.fornecedor_id
                context['identificadorCompra'] = compra.identificadorCompra
                context['idConta'] = compra.conta_id
                context['compra_identificada'] = listarProdutosTemplate
                context['dolarMedio'] = compra.valorDolarMedio
                context['produtos'] = Produto.objects.all().order_by('NomeProduto')

        if self.request.GET.__contains__("id_fornecedor_cadastro"):
            listarProdutosTemplate = []
            identificadorCompra = 0
            context['id_fornecedor_cadastro'] = int(self.request.GET["id_fornecedor_cadastro"])

        context['compras'] = Compra.objects.all()
        context['mensagem'] = ''
        # Popular template
        context['fornecedores'] = Fornecedor.objects.all()

        if self.request.resolver_match.url_name == "fazercompraspecas":
            context['produtos'] = Produto.objects.all().filter(categoria_id=5).order_by('NomeProduto')
        if self.request.resolver_match.url_name == "fazercomprasaparelhos":
            context['produtos'] = Produto.objects.all().filter(categoria_id__lte=4).order_by('NomeProduto')
            logging.warning(context['produtos'])
        context['tipo_produto'] = self.request.resolver_match.url_name
        context['localizacaoCompra'] = LocalizacaoCompra.objects.all()
        context['contasDetalhadas'] = financeiro.saldo_conta
        return context

    def post(self, request, *args, **kwargs):
        context = super(FazerComprasView, self).get_context_data(**kwargs)
        financeiro = MovimentacaoFinanceira()
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
        identificadorCompra = self.request.POST.getlist('identificadorCompra')
        cotacaoDolar = self.request.POST.getlist('dolarMedio')
        tipo_produto = self.request.POST.getlist('tipo_produto')
        #cotacaoDolar = financeiro.dolarMedio(,contaOrigemOriginal)
        descricao = self.request.POST.getlist('descricao')
        localizacaoCompra = Fornecedor.objects.get(id=fornecedor[0])

        dataModificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', dataCompra[0])
        contador = 0
        valorCompra = 0
        valorEstornoCompra = 0

        # Desabilitando registro de Compra Salva caso função seja editar
        if identificadorCompra[0] != "":
            logging.warning(identificadorCompra[0])
            compraDesabilitada = Compra.objects.filter(identificadorCompra=identificadorCompra[0],ativo=True)
            #Devolvendo o dinheiro da Compra para a conta especifica
            for compra in compraDesabilitada:
                valorEstornoCompra = valorEstornoCompra + compra.quantidadeProduto*compra.precoProduto
            itinerario_compra = Deslocamento.objects.filter(identificadorCompra=identificadorCompra[0],ativo=True)
            proximaCompra = identificadorCompra[0]
            for cidade in itinerario_compra:
                estorno_frete = MovimentacaoConta.objects.filter(id=cidade.idMovimentacaoConta)
                estorno_frete_movimentacao_conta = MovimentacaoConta (
                    criados=str(dataModificada),
                    contaCredito_id=estorno_frete.contaDebito,
                    valorCredito=estorno_frete.valorDebito,
                    identificadorCompra=str(proximaCompra),
                    descricao=descricao,
                )
                estorno_frete_movimentacao_conta.save()
                estorno_frete.delete()
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
        tipoConta = Conta.objects.get(id=contaOrigem[0])
        identificadorDolar = False
        if tipoConta.categoria_id == 4 or tipoConta.categoria_id == 5:
            identificadorDolar = True
        else:
            #Compra em real
            cotacaoDolar = 1

        for produto in produtos:
            if precos[contador] != "" and quantidades[contador] != "":
                formCompra = Compra(
                    criados=str(dataModificada),
                    quantidadeProduto=quantidades[contador],
                    precoProduto=precos[contador],
                    identificadorCompra=str(proximaCompra),
                    fornecedor_id=fornecedor[0],
                    produto_id=produto,
                    descricao=descricao,
                    idLocalizacao_id=localizacaoCompra.localizacaoCompra_id,
                    conta_id=contaOrigem[0],
                    valorDolarMedio=float(cotacaoDolar)
                )
                valorCompra = valorCompra + float(precos[contador]) * float(quantidades[contador])
                formCompra.save()
                contador = contador + 1
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

        # Colocando o local inicial
        formDeslocamento = Deslocamento(
            criados=str(dataModificada),
            destino=localizacaoCompra.localizacaoCompra_id,
            frete="0",
            identificadorCompra=str(proximaCompra),
        )
        formDeslocamento.save()

        context['mensagem'] = 'Compra Salva'

        # Popular template
        context['fornecedores'] = Fornecedor.objects.all()
        logging.warning("Tipo Produto")
        logging.warning(tipo_produto)
        if tipo_produto[0] == "fazercompraspecas":
            context['produtos'] = Produto.objects.all().filter(categoria_id=5).order_by('NomeProduto')
        if tipo_produto[0] == "fazercomprasaparelhos":
            context['produtos'] = Produto.objects.all().filter(categoria_id__lte=4).order_by('NomeProduto')
        context['tipo_produto'] = tipo_produto[0]

        context['localizacaoCompra'] = LocalizacaoCompra.objects.all()
        context['contasDetalhadas'] = financeiro.saldo_conta
        context['dolarMedio'] = financeiro.dolarMedio
        return HttpResponseRedirect('/'+tipo_produto[0]+'/?venda_realizada=1', context)



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
                    localizacao_compra = Deslocamento.objects.filter(identificadorCompra=self.request.GET["idCompra"])
                    for local in localizacao_compra:
                        if local.destino == 7:
                            atualizarEstoque = Produto.objects.get(id=apagarcompra.produto_id)
                            atualizarEstoque.estoque = atualizarEstoque.estoque - apagarcompra.quantidadeProduto
                            atualizarEstoque.save()
                    apagar.delete()
                apagarmovimentacao = MovimentacaoConta.objects.filter(identificadorCompra=self.request.GET["idCompra"])
                apagarmovimentacao.delete()
                apagardeslocamento = Deslocamento.objects.filter(identificadorCompra=self.request.GET["idCompra"])
                apagardeslocamento.delete()

        hoje = timezone.now().date()
        quinze_dias_atras = hoje - timedelta(days=15)
        compras = Compra.objects.order_by('-identificadorCompra').filter(ativo=True, criados__gte=quinze_dias_atras)

        listarComprasTemplate = []
        identificadorCompra = 0
        moeda = ""
        for compra in compras:
            #Se a compra advir de uma venda de aparelho, não listar.
            if compra.conta_id == -1:
                continue

            if identificadorCompra != compra.identificadorCompra:
                compraIdentificada = Compra.objects.filter(identificadorCompra=compra.identificadorCompra, ativo=True)
                valorCompraTotal = 0

                for compra in compraIdentificada:
                    valorCompraTotal = valorCompraTotal + compra.quantidadeProduto * compra.precoProduto
                itinerario_compra = Deslocamento.objects.filter(identificadorCompra=compra.identificadorCompra).order_by('-id')
                cidade_atual = ""

                for cidade in itinerario_compra:
                    localizacao = LocalizacaoCompra.objects.get(id=cidade.destino)
                    cidade_atual = localizacao.localizacaoCompra
                    break

                if compra.valorDolarMedio == 1:
                    moeda="R$"
                else:
                    moeda="US$"

                listarComprasTemplate.append(
                    {
                        'idCompra': compra.identificadorCompra,
                        'fornecedor': compra.fornecedor,
                        'dataCompra': compra.criados,
                        'valorCompra': valorCompraTotal,
                        'localizacaoCompra': cidade_atual,
                        'moeda': moeda,
                    }
                )
                valorCompraTotal = 0
                identificadorCompra = compra.identificadorCompra
        context['listarCompras'] = listarComprasTemplate

        return (context)

    def post(self, request, *args, **kwargs):
        context = super(ListarComprasView, self).get_context_data(**kwargs)
        data_inicio = self.request.POST.getlist('data_inicio')
        data_fim = self.request.POST.getlist('data_fim')
        cliente = self.request.POST.getlist('cliente')
        data_inicio = datetime.strptime(data_inicio[0], '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim[0], '%Y-%m-%d').date()
        compras = Compra.objects.order_by('-identificadorCompra').filter(
            ativo=True,
            criados__range=[data_inicio,data_fim],
        )

        listarComprasTemplate = []
        identificadorCompra = 0
        moeda = ""
        for compra in compras:
            #Se a compra advir de uma venda de aparelho, não listar.
            if compra.conta_id == -1:
                continue

            if identificadorCompra != compra.identificadorCompra:
                compraIdentificada = Compra.objects.filter(identificadorCompra=compra.identificadorCompra, ativo=True)
                valorCompraTotal = 0

                for compra in compraIdentificada:
                    valorCompraTotal = valorCompraTotal + compra.quantidadeProduto * compra.precoProduto
                itinerario_compra = Deslocamento.objects.filter(identificadorCompra=compra.identificadorCompra).order_by('-id')
                cidade_atual = ""

                for cidade in itinerario_compra:
                    localizacao = LocalizacaoCompra.objects.get(id=cidade.destino)
                    cidade_atual = localizacao.localizacaoCompra
                    break

                if compra.valorDolarMedio == 1:
                    moeda="R$"
                else:
                    moeda="US$"

                listarComprasTemplate.append(
                    {
                        'idCompra': compra.identificadorCompra,
                        'fornecedor': compra.fornecedor,
                        'dataCompra': compra.criados,
                        'valorCompra': valorCompraTotal,
                        'localizacaoCompra': cidade_atual,
                        'moeda': moeda,
                    }
                )
                valorCompraTotal = 0
                identificadorCompra = compra.identificadorCompra
        context['listarCompras'] = listarComprasTemplate
        return render(request, 'listarcompras.html', context)


class LocalizacaoCompraView(TemplateView):
    template_name = 'localizacaocompra.html'
    def get_context_data(self, **kwargs):
        context = super(LocalizacaoCompraView, self).get_context_data(**kwargs)
        financeiro = MovimentacaoFinanceira()
        if self.request.GET.__contains__("idDeslocamento"):
            if self.request.GET["funcao"] == "apagar":
                apagarMovimentacao = MovimentacaoConta(id=self.request.GET["idMovimentacaoConta"])
                apagarMovimentacao.delete()
                apagarDeslocamento = Deslocamento(id=self.request.GET["idDeslocamento"])
                apagarDeslocamento.delete()
        localizacao_compra = Deslocamento.objects.filter(identificadorCompra = self.request.GET["idCompra"]).order_by('-id')
        compra_deslocada = 0
        apagar_apenas_ultimo = 1
        localizacao_detalhada = []
        for localizacao in localizacao_compra:
            if compra_deslocada == 0:
                origem = localizacao.destino
                compra_deslocada = 1
            try:
                origem_itinerario = LocalizacaoCompra.objects.get(id=localizacao.origem)
                destino_itinerario = LocalizacaoCompra.objects.get(id=localizacao.destino)
                localizacao_detalhada.append(
                    {
                     "id": localizacao.id,
                    "origem": origem_itinerario.localizacaoCompra,
                    "destino": destino_itinerario.localizacaoCompra,
                    "frete": localizacao.frete,
                    "data": localizacao.criados,
                    "id_movimentacao_conta": localizacao.idMovimentacaoConta,
                    "apagar_apenas_ultimo": apagar_apenas_ultimo,
                    }
                )
            except:
                pass

            apagar_apenas_ultimo = 0

        if compra_deslocada == 0:
            logging.warning("Except")
            localizacao_compra = Compra.objects.filter(identificadorCompra = self.request.GET["idCompra"]).order_by('-id')
            for localizacao in localizacao_compra:
                origem = localizacao.idLocalizacao_id
                break
        context['origem_localizacao'] = origem
        context['localizacao_compra'] = LocalizacaoCompra.objects.all()
        context['itinerario'] = localizacao_detalhada
        context['contas_detalhadas'] = financeiro.saldo_conta
        context['id_compra'] = self.request.GET["idCompra"]
        context['apagar_ultimo'] = "1"
        return(context)

    def post(self, request, *args, **kwargs):
        context = super(LocalizacaoCompraView, self).get_context_data(**kwargs)
        financeiro = MovimentacaoFinanceira()
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        # Debitando frete da conta
        conta_em_dolar = 0
        #cotacao_dolar = 1 indica pagamento em real
        cotacao_dolar = 1
        conta_debito = Conta.objects.get(id=self.request.POST.get('conta'))
        if conta_debito.categoria_id == 4 or conta_debito.categoria_id == 5:
            conta_em_dolar = 1
            cotacao_dolar = financeiro.dolarMedio()

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
        logging.warning("Movimentacao id")
        logging.warning(formMovimentacao.id)
        formDeslocamento = Deslocamento(
            criados=hoje,
            origem=self.request.POST.get('origem'),
            destino=self.request.POST.get('destino'),
            frete=self.request.POST.get('valor_frete'),
            identificadorCompra=self.request.POST.get('id_compra'),
            idMovimentacaoConta=formMovimentacao.id,
        )
        formDeslocamento.save()

        # Atualizando o estoque Destino Sobral (7) modificar para ficar dinâmico
        if self.request.POST.get('destino') == "7":
            produtos_comprados = Compra.objects.filter(identificadorCompra=self.request.POST.get('id_compra'))
            contador = 0
            for produto_comprado in produtos_comprados:
                atualizarEstoque = Produto.objects.get(id=produto_comprado.produto_id)
                atualizarEstoque.estoque = atualizarEstoque.estoque + produto_comprado.quantidadeProduto
                atualizarEstoque.save()
                contador = contador + 1
        return HttpResponseRedirect('/listarcompras/', context)

class AdicionarLocalizacao(TemplateView):
    template_name = 'adicionarlocalizacao.html'
    def get_context_data(self, **kwargs):
        context = super(AdicionarLocalizacao, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        context = super(AdicionarLocalizacao, self).get_context_data(**kwargs)