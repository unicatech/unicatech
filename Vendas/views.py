from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Sum

from datetime import date, datetime
import re
import logging

from .models import Venda
from Produtos.models import Produto
from Contas.models import MovimentacaoConta, Conta, Cartao, RecebimentoCartao
from Vendas.models import Cliente
from Compras.models import Compra
# Create your views here.

class FazerVendasView(TemplateView):

    template_name = 'fazervendas.html'
    def get_context_data(self, **kwargs):
        context = super(FazerVendasView, self).get_context_data(**kwargs)
        context['editarVenda'] = 0
        context['dataVenda'] = datetime.now().strftime("%d-%m-%Y")
        if self.request.GET.__contains__("venda_realizada"):
            logging.warning("Venda Realizada")
            context['venda_realizada'] = 1

        if self.request.GET.__contains__("idVenda"):
            vendas = Venda.objects.filter(identificadorVenda=self.request.GET["idVenda"],ativo=True)
            listarProdutosTemplate = []
            identificadorVenda = 0
            valorCompraVenda = 0
            context['editarVenda'] = 1

            for venda in vendas:
                listarProdutosTemplate.append(
                    {
                     'idProduto': venda.produto_id,
                     'quantidadeProduto': venda.quantidadeProduto,
                     'precoProduto': venda.precoProduto,
                     }
                )
                context['dataVenda'] = venda.criados.strftime('%d-%m-%Y')
                context['idCliente'] = venda.cliente_id
                context['identificadorVenda'] = venda.identificadorVenda
                context['venda_identificada'] = listarProdutosTemplate
                context['descricao'] = venda.descricao

        context['vendas'] = Venda.objects.all()
        context['mensagem'] = ''
        #Popular template
        context['clientes'] = Cliente.objects.filter().order_by('nomeCliente')

        # Se a função for "Editar Venda" permita que apareça o produto com estoque zerado (afinal já está na venda) mas não negativo
        if context['editarVenda'] == 1:
            context['produtos'] = Produto.objects.all().filter(estoque__gte=0).order_by('NomeProduto')
        else:
            context['produtos'] = Produto.objects.all().filter(estoque__gt=0).order_by('NomeProduto')

        context['produtos_compra'] = Produto.objects.all().order_by('NomeProduto')
        return context

    def post(self, request, *args, **kwargs):
        context = super(FazerVendasView, self).get_context_data(**kwargs)

        try:
            ultimaVenda = Venda.objects.order_by('-identificadorVenda')
            id = 0
            for identificador in ultimaVenda:
                id = identificador.identificadorVenda
                break
            proximaVenda = id + 1
        except:
            proximaVenda = 1

        cliente = self.request.POST.getlist('cliente')
        dataVenda = self.request.POST.getlist('dataVenda')
        produtos = self.request.POST.getlist('produto')
        quantidades = self.request.POST.getlist('qtde')
        quantidades_compra = self.request.POST.getlist('quantidade_compra')
        precos = self.request.POST.getlist('preco')
        precos_compra = self.request.POST.getlist('preco_compra')
        identificadorVenda = self.request.POST.getlist('identificadorVenda')
        descricao = self.request.POST.getlist('descricao')
        gerar_compra = self.request.POST.get('gerar_compra')
        produtos_compra = self.request.POST.getlist('produto_compra')
        dataModificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', dataVenda[0])

        contador = 0
        valorVenda = 0
        valorEstorno = 0
        #Caso a entrada nova possua mais de um registro
        produtos_repetidos = []
        #Caso a entrada nova possua mais de 1 registro e a antiga possua apenas 1
        produtos_repetidos_unicos = []
        #Produtos removidos da venda
        produtos_removidos_venda = []
        quantidade_original_produto_vendido = 0
        # Desabilitando registro de Venda Salva caso função seja editar
        if identificadorVenda[0] != "":
            #Verificando se há algum produto que foi vendido e foi removido
            produtos_vendidos = Venda.objects.filter(identificadorVenda=identificadorVenda[0],
                                                  ativo=True)
            for produto_vendido in produtos_vendidos:
                produto_encontrado = 0
                for produto in produtos:
                    if produto_vendido.produto_id == produto:
                        logging.warning("Produto encontrado")
                        produto_encontrado = 1
                if produto_encontrado == 0:
                    produtos_removidos_venda.append(produto_vendido.produto_id)

            for produto in produtos:
                try:
                    logging.warning("Try")
                    for produto_repetido_unico in produtos_repetidos_unicos:
                        if produto_repetido_unico == produto:
                            produto = -1
                            continue
                    if produto == -1:
                        continue
                    quantidadeOriginalEstoque = Venda.objects.get(identificadorVenda=identificadorVenda[0],
                                                              produto_id=produto,ativo=True)
                    atualizarEstoque = Produto.objects.get(id=produto)
                    atualizarEstoque.estoque = atualizarEstoque.estoque + quantidadeOriginalEstoque.quantidadeProduto
                    atualizarEstoque.save()
                    produtos_repetidos_unicos.append(produto)
                except:
                    logging.warning("Except")
                    for produto_repetido in produtos_repetidos:
                        if produto_repetido == produto:
                            produto = -1
                            continue
                    if produto == -1:
                        continue

                    try:
                        venda_original = Venda.objects.filter(identificadorVenda=identificadorVenda[0],
                                                              produto_id=produto, ativo=True).aggregate(Sum('quantidadeProduto'))
                        quantidade_original_produto_vendido = int(venda_original["quantidadeProduto__sum"])
                    except:
                        quantidade_original_produto_vendido = 0

                    atualizarEstoque = Produto.objects.get(id=produto)
                    atualizarEstoque.estoque = atualizarEstoque.estoque + quantidade_original_produto_vendido
                    atualizarEstoque.save()
                    produtos_repetidos.append(produto)

            Venda.objects.filter(identificadorVenda=identificadorVenda[0]).update(ativo=False)
            proximaVenda = identificadorVenda[0]

        # Salvando Venda
        contador = 0
        estoque_anterior = 0
        for produto in produtos:
           if precos[contador] != "" and quantidades[contador] != "":
                #Removendo do estoque
                atualizarEstoque = Produto.objects.get(id=produto)
                estoque_anterior = atualizarEstoque.estoque
                atualizarEstoque.estoque = atualizarEstoque.estoque - int(float(quantidades[contador]))
                atualizarEstoque.save()
                #Calculando o lucro
                compras_produto = Compra.objects.filter(produto_id=atualizarEstoque.id, ativo=True).order_by('-id')
                #Calculando preço médio do estoque (média móvel)
                compra_total_produto = 0
                estoque_preco_medio = estoque_anterior
                quantidade_produto = 0
                frete_deslocamento = 0
                frete_medio_produto = 0
                for compra in compras_produto:
                    try:
                        deslocamentos = Deslocamento.objects.filter(identificadorCompra=compra.identificadorCompra)
                        for deslocamento in deslocamentos:
                            frete_deslocamento = frete_deslocamento + deslocamento.frete
                        frete_deslocamento = frete_deslocamento + compra.frete * compra.valorDolarMedio
                    except:
                        pass
                    if compra.quantidadeProduto >= estoque_preco_medio:
                        compra_total_produto = (compra_total_produto +
                                                estoque_preco_medio *
                                                float(compra.precoProduto) * compra.valorDolarMedio)
                        quantidade_produto = quantidade_produto + estoque_preco_medio
                        frete_medio_produto = frete_deslocamento / quantidade_produto
                        break
                    else:
                        compra_total_produto = (compra_total_produto +
                                                compra.quantidadeProduto * compra.precoProduto * compra.valorDolarMedio)
                        estoque_preco_medio = estoque_preco_medio - compra.quantidadeProduto
                        quantidade_produto = quantidade_produto + compra.quantidadeProduto
                #Prevenir quando o estoque foi adicionado no cadastro do produto, pois o valor vai vir menor que zero
                if quantidade_produto > 0:
                    preco_medio = compra_total_produto / quantidade_produto
                else:
                    preco_medio = 0
                lucro = float(quantidades[contador]) * (float(precos[contador]) - preco_medio)
                # Prevenir quando a quantidade comprada não estiver cadastrada, pois o valor vai vir menor que zero
                if quantidade_produto > 0:
                    lucro = lucro - frete_medio_produto

                #Cadastrando Venda
                if produto != 0:
                    formVenda = Venda(
                                 criados=str(dataModificada),
                                 quantidadeProduto=quantidades[contador],
                                 precoProduto=precos[contador],
                                 identificadorVenda=str(proximaVenda),
                                 cliente_id=cliente[0],
                                 produto_id=produto,
                                 lucro=lucro,
                                 descricao=descricao[0],
                    )
                    formVenda.save()

                valorVenda = valorVenda + float(precos[contador])*float(quantidades[contador])
                contador = contador + 1

        context['mensagem'] = 'Venda Salva'

        if gerar_compra == "on":
            logging.warning("Gerou")
            try:
                ultimaCompra = Compra.objects.last()
                proximaCompra = ultimaCompra.identificadorCompra + 1
            except:
                proximaCompra = 1
            contador = 0
            identificadorDolar = False
            cotacaoDolar = 1
            valorCompra = 0
            logging.warning(produtos_compra)
            for produto in produtos_compra:
                if precos_compra[contador] != "" and quantidades_compra[contador] != "":
                    formCompra = Compra(
                    criados=str(dataModificada),
                    quantidadeProduto=quantidades_compra[contador],
                    precoProduto=precos_compra[contador],
                    identificadorCompra=str(proximaCompra),
                    fornecedor_id=0,
                    produto_id=produto,
                    descricao="Recebimento de Aparelho",
                    idLocalizacao_id=7,
                    conta_id=-1, #recebimento de aparelho
                    valorDolarMedio=float(cotacaoDolar)
                    )
                    valorCompra = valorCompra + float(precos_compra[contador]) * float(quantidades_compra[contador])
                    formCompra.save()
                    #Atualizando o estoque
                    logging.warning("Adicionando")
                    atualizarEstoque = Produto.objects.get(id=produto)
                    atualizarEstoque.estoque = atualizarEstoque.estoque + int(float(quantidades[contador]))
                    atualizarEstoque.save()
                    contador = contador + 1

            # Debitando da conta
            formMovimentacao = MovimentacaoConta(
                    criados=str(dataModificada),
                    contaDebito=-1,
                    valorDebito=valorCompra,
                    identificadorCompra=str(proximaCompra),
                    identificadorVenda=str(proximaVenda),
                    descricao="Recebimento de Aparelho",
                    cotacaoDolar=float(cotacaoDolar),
                    identificadorDolar=identificadorDolar,
            )
            formMovimentacao.save()

            #Creditando aparelho recebido
            dataform = MovimentacaoConta(contaCredito_id=-1,
                                         criados=dataModificada,
                                         valorCredito=valorCompra,
                                         identificadorVenda=str(proximaVenda),
                                         descricao="Recebimento de Aparelho",
                                         identificadorDolar=False,
                                         )
            dataform.save()

        return HttpResponseRedirect('/fazervendas/?venda_realizada=1', context)

class ListarVendasView(TemplateView):

    template_name = 'listarvendas.html'

    def get_context_data(self, **kwargs):
        context = super(ListarVendasView, self).get_context_data(**kwargs)
        produtos_repetidos = []
        context['mensagem'] = ''
        if self.request.GET.__contains__("idVenda"):
            if self.request.GET["funcao"] == "apagar":
                logging.warning(self.request.GET["idVenda"])
                apagarvendas = Venda.objects.filter(identificadorVenda=self.request.GET["idVenda"],ativo=True)
                produto = 0
                for apagarvenda in apagarvendas:
                    #Retorna aparelhos pro estoque
                    try:
                        logging.warning("Try")
                        quantidadeOriginalEstoque = Venda.objects.get(identificadorVenda=self.request.GET["idVenda"],
                                                                  produto_id=apagarvenda.produto_id,
                                                                  ativo=True)
                        atualizarEstoque = Produto.objects.get(id=apagarvenda.produto_id)
                        atualizarEstoque.estoque = atualizarEstoque.estoque + quantidadeOriginalEstoque.quantidadeProduto
                        atualizarEstoque.save()
                    except:
                        logging.warning("Except")
                        for produto_repetido in produtos_repetidos:
                             if produto_repetido == apagarvenda.produto_id:
                                 produto = -1
                                 continue
                        if produto == -1:
                            produto = 0
                            continue
                        quantidadeOriginalEstoque = Venda.objects.filter(identificadorVenda=self.request.GET["idVenda"],
                                                              produto_id=apagarvenda.produto_id,
                                                             ativo=True).aggregate(Sum('quantidadeProduto'))
                        atualizarEstoque = Produto.objects.get(id=apagarvenda.produto_id)
                        atualizarEstoque.estoque = (atualizarEstoque.estoque +
                                                    quantidadeOriginalEstoque["quantidadeProduto__sum"])
                        atualizarEstoque.save()
                        produtos_repetidos.append(apagarvenda.produto_id)
                #Apaga venda (soft delete)
                Venda.objects.filter(identificadorVenda=self.request.GET["idVenda"]).update(ativo=False)
                MovimentacaoConta.objects.filter(identificadorVenda=self.request.GET["idVenda"]).update(ativo=False)
                #Se houver compra na venda a ser apagada também apagar compra (soft delete)
                compras_em_venda = MovimentacaoConta.objects.filter(identificadorVenda=self.request.GET["idVenda"])
                for compra in compras_em_venda:
                    if compra.identificadorCompra != "0":
                        pass
                        #remover_produto_compra = Compra.objects.filter(identificadorCompra=compra.identificadorCompra)
                        #for produto_comprado in remover_produto_compra:
                        #    atualizarEstoque = Produto.objects.get(id=produto_comprado.produto)
                        #    atualizarEstoque.estoque = atualizarEstoque.estoque - produto_comprado.quantidadeProduto
                        #    atualizarEstoque.save()
                        #Compra.objects.filter(identificadorCompra=compra.identificadorCompra).update(ativo=False)

        vendas = Venda.objects.order_by('-identificadorVenda').filter(ativo=True)

        listarVendasTemplate = []
        recebimentos = []
        identificadorVenda = 0
        valor_recebido_venda = 0
        for venda in vendas:
            if identificadorVenda != venda.identificadorVenda:
                vendaIdentificada = Venda.objects.filter(identificadorVenda=venda.identificadorVenda,ativo=True).order_by('-identificadorVenda')
                valorVendaTotal = 0
                for venda in vendaIdentificada:
                    valorVendaTotal = valorVendaTotal + venda.quantidadeProduto * venda.precoProduto
                recebimentos_venda = MovimentacaoConta.objects.filter(
                    identificadorVenda=venda.identificadorVenda,
                    identificadorCompra=0,
                    ativo=True)
                #logging.warning("Identificador Venda:" +" "+str(venda.identificadorVenda))
                for recebimento_venda in recebimentos_venda:
                    recebimentos.append({
                            'valor_recebimento': recebimento_venda.valorCredito,
                            'data': recebimento_venda.criados,
                            'Credito': recebimento_venda.contaCredito,
                            'identificador_parcela': recebimento_venda.id,
                    })
                    valor_recebido_venda = valor_recebido_venda + recebimento_venda.valorCredito

                total_a_receber = valorVendaTotal - valor_recebido_venda
                listarVendasTemplate.append(
                    {
                        'idVenda': venda.identificadorVenda,
                        'cliente': venda.cliente,
                        'dataVenda': venda.criados,
                        'valorVenda': valorVendaTotal,
                        'recebimentos': recebimentos,
                        'total_a_receber': total_a_receber,
                     }
                )
                valor_recebido_venda = 0
                recebimentos = []
                identificadorVenda = venda.identificadorVenda
        context['listarVendas'] = listarVendasTemplate
        return(context)

class ParcelasReceberView(TemplateView):

    template_name = 'parcelasareceber.html'
    def get_context_data(self, **kwargs):
        context = super(ParcelasReceberView, self).get_context_data(**kwargs)
        context['mensagem'] = ''

        if self.request.GET.__contains__("parcelarecebida"):
            context['mensagem'] = 'Parcela Recebida'
        if self.request.GET.__contains__("id"):
            if self.request.GET["funcao"] == "apagar":
                MovimentacaoConta.objects.filter(id=self.request.GET["id"]).delete()
                context['mensagem'] = "Recebimento Apagado"

        vendas = Venda.objects.order_by('identificadorVenda').filter(ativo=True)

        listarVendasTemplate = []
        recebimentos = []
        identificadorVenda = 0
        valor_recebido_venda = 0
        for venda in vendas:
            if identificadorVenda != venda.identificadorVenda:
                vendaIdentificada = Venda.objects.filter(identificadorVenda=venda.identificadorVenda,ativo=True)
                valorVendaTotal = 0
                for venda in vendaIdentificada:
                    valorVendaTotal = valorVendaTotal + venda.quantidadeProduto * venda.precoProduto
                recebimentos_venda = MovimentacaoConta.objects.filter(
                    identificadorVenda=venda.identificadorVenda,
                    identificadorCompra=0,
                    ativo=True)

                for recebimento_venda in recebimentos_venda:
                    recebimentos.append({
                            'valor_recebimento': recebimento_venda.valorCredito,
                            'data': recebimento_venda.criados,
                            'Credito': recebimento_venda.contaCredito,
                            'identificador_parcela': recebimento_venda.id,
                    })
                    valor_recebido_venda = valor_recebido_venda + recebimento_venda.valorCredito
                total_a_receber = valorVendaTotal - valor_recebido_venda
                if total_a_receber > 0:
                    listarVendasTemplate.append(
                        {
                        'idVenda': venda.identificadorVenda,
                        'cliente': venda.cliente,
                        'dataVenda': venda.criados,
                        'valorVenda': valorVendaTotal,
                        'recebimentos': recebimentos,
                        'total_a_receber': total_a_receber,
                        }
                    )
                valor_recebido_venda = 0
                recebimentos = []
                valorVendaTotal = 0
                identificadorVenda = venda.identificadorVenda
        context['listarVendas'] = listarVendasTemplate
        return(context)

class ParcelasReceberModalView(TemplateView):

    template_name = 'parcelasarecebermodal.html'
    def get_context_data(self, **kwargs):
        context = super(ParcelasReceberModalView, self).get_context_data(**kwargs)
        context['mensagem'] = ''
        context['data_recebimento'] = datetime.now().strftime("%d-%m-%Y")
        venda_recebimento = Venda.objects.filter(identificadorVenda=self.request.GET["idVenda"],ativo=True)
        recebimentos_venda = MovimentacaoConta.objects.filter(identificadorVenda=self.request.GET["idVenda"], ativo=True)
        recebimento = 0
        for recebimento_venda in recebimentos_venda:
               recebimento = recebimento + recebimento_venda.valorCredito

        valor_venda_total = 0.0
        total_receber = 0.0

        for venda in venda_recebimento:
            valor_venda_total = valor_venda_total + venda.quantidadeProduto * venda.precoProduto
            total_receber = valor_venda_total - recebimento

            listarVendasTemplate = {
                'idVenda': venda.identificadorVenda,
                'cliente': venda.cliente.nomeCliente,
                'dataVenda': venda.criados,
                'valorVenda': valor_venda_total,
                'total_receber': total_receber,
            }

        context['listarVendas'] = listarVendasTemplate

        contasDetalhadas = Conta.objects.all().filter(id__gt=0)
        contaCredito = []
        for conta in contasDetalhadas:
            if conta.categoria_id <= 3 and conta.categoria_id >= 1:
                moeda = 'R$'
                contaCredito.append({'id': conta.id, 'nomeConta': conta.nomeConta})

        context['contaCredito'] = contaCredito
        return(context)

    def post(self, request, *args, **kwargs):

        context = super(ParcelasReceberModalView, self).get_context_data(**kwargs)
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        data_recebimento = self.request.POST.getlist('data_recebimento')
        data_modificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', data_recebimento[0])
        conta_recebimento = Conta.objects.get(id=self.request.POST.get('contaCredito'), ativo=True)
        taxa = 0
        if conta_recebimento.categoria_id == 1:
            logging.warning("Cartão de crédito")
            logging.warning(f'Parcelas do Cartão:{self.request.POST.get("parcelaCartao")}')
            conta_cartao = Cartao.objects.get(cartao=conta_recebimento.cartao)
            # Quando migrar para o Python 3.10 utilizar match(equivalente do switch em C)
            if self.request.POST.get("parcelaCartao") == "1":
                taxa = float(conta_cartao.taxa_cartao1)
            elif self.request.POST.get("parcelaCartao") == "2":
                taxa = float(conta_cartao.taxa_cartao2)
            elif self.request.POST.get("parcelaCartao") == "3":
                taxa = float(conta_cartao.taxa_cartao3)
            elif self.request.POST.get("parcelaCartao") == "4":
                taxa = float(conta_cartao.taxa_cartao4)
            elif self.request.POST.get("parcelaCartao") == "5":
                taxa = float(conta_cartao.taxa_cartao5)
            elif self.request.POST.get("parcelaCartao") == "6":
                taxa = float(conta_cartao.taxa_cartao6)
            elif self.request.POST.get("parcelaCartao") == "7":
                taxa = float(conta_cartao.taxa_cartao7)
            elif self.request.POST.get("parcelaCartao") == "8":
                taxa = float(conta_cartao.taxa_cartao8)
            elif self.request.POST.get("parcelaCartao") == "9":
                taxa = float(conta_cartao.taxa_cartao9)
            elif self.request.POST.get("parcelaCartao") == "10":
                taxa = float(conta_cartao.taxa_cartao10)
            elif self.request.POST.get("parcelaCartao") == "11":
                taxa = float(conta_cartao.taxa_cartao11)
            elif self.request.POST.get("parcelaCartao") == "12":
                taxa = float(conta_cartao.taxa_cartao12)
            elif self.request.POST.get("parcelaCartao") == "13":
                taxa = float(conta_cartao.taxa_cartao13)
            elif self.request.POST.get("parcelaCartao") == "14":
                taxa = float(conta_cartao.taxa_cartao14)
            elif self.request.POST.get("parcelaCartao") == "15":
                taxa = float(conta_cartao.taxa_cartao15)
            elif self.request.POST.get("parcelaCartao") == "16":
                taxa = float(conta_cartao.taxa_cartao16)
            elif self.request.POST.get("parcelaCartao") == "17":
                taxa = float(conta_cartao.taxa_cartao17)
            elif self.request.POST.get("parcelaCartao") == "18":
                taxa = float(conta_cartao.taxa_cartao18)
            elif self.request.POST.get("parcelaCartao") == "0":
                taxa = float(conta_cartao.taxa_debito)
            valor_recebimento = (1 - taxa / 100) * float(self.request.POST.get('valorRecebido'))
            dataform = RecebimentoCartao(conta_cartao_id=self.request.POST.get('contaCredito'),
                                     criados=data_modificada,
                                     valor=self.request.POST.get('valorRecebido'),
                                     parcelas=self.request.POST.get('parcelaCartao'),
                                     bandeira=self.request.POST.get('bandeira'),
                                     identificador_venda=self.request.POST.get('identificadorVenda'),
                                     valor_liquido=valor_recebimento
            )
            dataform.save()
        elif conta_recebimento.categoria_id == 2:
            logging.warning("Depósito em real")
            valor_recebimento = float(self.request.POST.get('valorRecebido'))
        elif conta_recebimento.categoria_id == 3:
            logging.warning("Espécie")
            valor_recebimento = float(self.request.POST.get('valorRecebido'))

        dataform = MovimentacaoConta(contaCredito_id=self.request.POST.get('contaCredito'),
                                     criados=data_modificada,
                                     contaDebito="0",
                                     valorCredito=valor_recebimento,
                                     identificadorVenda=self.request.POST.get('identificadorVenda'),
                                     descricao=self.request.POST.get('descricao'),
                                     identificadorDolar=False,
        )
        dataform.save()

        context['mensagem'] = "Recebimento Efetuado"
        #return super(TemplateView, self).render_to_response(context)
        return HttpResponseRedirect("/parcelasareceber/?parcelarecebida=1")


