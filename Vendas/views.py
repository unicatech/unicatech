from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from datetime import date, datetime
import re
import logging

from .models import Venda
from Produtos.models import Produto
from Contas.models import MovimentacaoConta, Conta, Cartao
from Vendas.models import Cliente
from Compras.models import Compra
# Create your views here.

class FazerVendasView(TemplateView):

    template_name = 'fazervendas.html'
    def get_context_data(self, **kwargs):
        context = super(FazerVendasView, self).get_context_data(**kwargs)
        context['editarVenda'] = 0
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

        context['vendas'] = Venda.objects.all()
        context['mensagem'] = ''
        #Popular template
        context['clientes'] = Cliente.objects.all()

        # Se a função for "Editar Venda" permita que apareça o produto com estoque zerado (afinal já está na venda) mas não negativo
        if context['editarVenda'] == 1:
            context['produtos'] = Produto.objects.all().filter(estoque__gte=0)
        else:
            context['produtos'] = Produto.objects.all().filter(estoque__gt = 0)

        return context

    def post(self, request, *args, **kwargs):
        context = super(FazerVendasView, self).get_context_data(**kwargs)

        try:
            ultimaVenda = Venda.objects.last()
            proximaVenda = ultimaVenda.identificadorVenda + 1
        except:
            proximaVenda = 1

        cliente = self.request.POST.getlist('cliente')
        dataVenda = self.request.POST.getlist('dataVenda')
        produtos = self.request.POST.getlist('produto')
        quantidades = self.request.POST.getlist('qtde')
        precos = self.request.POST.getlist('preco')
        identificadorVenda = self.request.POST.getlist('identificadorVenda')
        descricao = self.request.POST.getlist('descricao')

        dataModificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', dataVenda[0])

        contador = 0
        valorVenda = 0
        valorEstorno = 0

        # Desabilitando registro de Venda Salva caso função seja editar
        if identificadorVenda[0] != "":
            for produto in produtos:
                atualizarEstoque = Produto.objects.get(id=produto)
                quantidadeOriginalEstoque = Venda.objects.get(identificadorVenda=identificadorVenda[0],produto_id=produto,ativo=True)
                atualizarEstoque.estoque = atualizarEstoque.estoque + quantidadeOriginalEstoque.quantidadeProduto
                atualizarEstoque.save()
                contador = contador + 1
                logging.warning(atualizarEstoque.NomeProduto)
                logging.warning(atualizarEstoque.estoque)
            Venda.objects.filter(identificadorVenda=identificadorVenda[0]).update(ativo=False)
            proximaVenda = identificadorVenda[0]

        # Salvando Venda
        contador = 0
        estoque_anterior = 0
        for produto in produtos:
           if precos[contador] != "" and quantidades[contador] != "":
                #Atualizando o estoque
                logging.warning("Removendo do Estoque")
                atualizarEstoque = Produto.objects.get(id=produto)
                estoque_anterior = atualizarEstoque.estoque
                atualizarEstoque.estoque = atualizarEstoque.estoque - int(float(quantidades[contador]))
                atualizarEstoque.save()
                #Calculando o lucro
                compras_produto = Compra.objects.filter(produto_id=atualizarEstoque.id, ativo=True).order_by('-id')
                estoque_produto = int(atualizarEstoque.estoque)
                #Calculando preço médio do estoque (média móvel)
                compra_total_produto = 0
                estoque_preco_medio = estoque_anterior
                quantidade_produto = 0
                for compra in compras_produto:
                    logging.warning(compra.identificadorCompra)
                    if compra.quantidadeProduto >= estoque_preco_medio:
                        compra_total_produto = (compra_total_produto +
                                                estoque_preco_medio *
                                                float(compra.precoProduto) * compra.valorDolarMedio)
                        quantidade_produto = quantidade_produto + estoque_preco_medio
                        break
                    else:
                        compra_total_produto = (compra_total_produto +
                                                compra.quantidadeProduto * compra.precoProduto * compra.valorDolarMedio)
                        estoque_preco_medio = estoque_preco_medio - compra.quantidadeProduto
                        quantidade_produto = quantidade_produto + compra.quantidadeProduto
                preco_medio = compra_total_produto / quantidade_produto
                lucro = float(quantidades[contador]) * (float(precos[contador]) - preco_medio)
                logging.warning(preco_medio)
                logging.warning(lucro)
                logging.warning(precos[contador])

                #Cadastrando Venda
                formVenda = Venda(
                             criados=str(dataModificada),
                             quantidadeProduto=quantidades[contador],
                             precoProduto=precos[contador],
                             identificadorVenda=str(proximaVenda),
                             cliente_id=cliente[0],
                             produto_id=produto,
                             lucro=lucro,
                )
                formVenda.save()

                valorVenda = valorVenda + float(precos[contador])*float(quantidades[contador])
                contador = contador + 1

        context['mensagem'] = 'Venda Salva'

        #Popular template
        context['clientes'] = Cliente.objects.all()
        context['produtos'] = Produto.objects.all().filter(estoque__gt = 0)

        return super(TemplateView, self).render_to_response(context)

class ListarVendasView(TemplateView):

    template_name = 'listarvendas.html'

    def get_context_data(self, **kwargs):
        context = super(ListarVendasView, self).get_context_data(**kwargs)

        context['mensagem'] = ''
        if self.request.GET.__contains__("idVenda"):
            if self.request.GET["funcao"] == "apagar":
                logging.warning(self.request.GET["idVenda"])
                apagarvendas = Venda.objects.filter(identificadorVenda=self.request.GET["idVenda"])
                for apagarvenda in apagarvendas:
                    #Retorna aparelhos pro estoque
                    quantidadeOriginalEstoque = Venda.objects.get(identificadorVenda=self.request.GET["idVenda"],
                                                                  produto_id=apagarvenda.produto_id, ativo=True)
                    atualizarEstoque = Produto.objects.get(id=apagarvenda.produto_id)
                    atualizarEstoque.estoque = atualizarEstoque.estoque + quantidadeOriginalEstoque.quantidadeProduto
                    atualizarEstoque.save()
                    #Apaga venda
                    apagar = Venda(id=apagarvenda.id)
                    apagar.delete()

        vendas = Venda.objects.order_by('identificadorVenda').filter(ativo=True)

        listarVendasTemplate = []
        identificadorVenda = 0
        for venda in vendas:
            if identificadorVenda != venda.identificadorVenda:
                vendaIdentificada = Venda.objects.filter(identificadorVenda=venda.identificadorVenda,ativo=True)
                valorVendaTotal = 0
                for venda in vendaIdentificada:
                    valorVendaTotal = valorVendaTotal + venda.quantidadeProduto * venda.precoProduto
                listarVendasTemplate.append(
                    {
                     'idVenda': venda.identificadorVenda,
                     'cliente': venda.cliente,
                     'dataVenda': venda.criados,
                     'valorVenda': valorVendaTotal,
                     }
                )
                valorVendaTotal = 0
                identificadorVenda = venda.identificadorVenda
        context['listarVendas'] = listarVendasTemplate
        return(context)

class ParcelasReceberView(TemplateView):

    template_name = 'parcelasareceber.html'
    def get_context_data(self, **kwargs):
        context = super(ParcelasReceberView, self).get_context_data(**kwargs)
        context['mensagem'] = ''

        vendas = Venda.objects.order_by('identificadorVenda').filter(ativo=True)

        listarVendasTemplate = []
        recebimentos = []
        identificadorVenda = 0
        for venda in vendas:
            if identificadorVenda != venda.identificadorVenda:
                vendaIdentificada = Venda.objects.filter(identificadorVenda=venda.identificadorVenda,ativo=True)
                valorVendaTotal = 0
                for venda in vendaIdentificada:
                    valorVendaTotal = valorVendaTotal + venda.quantidadeProduto * venda.precoProduto
                recebimentos_venda = MovimentacaoConta.objects.filter(identificadorVenda=venda.identificadorVenda,ativo=True)
                for recebimento_venda in recebimentos_venda:
                    recebimentos.append({
                            'valor_recebimento': recebimento_venda.valorCredito,
                            'data': recebimento_venda.criados,
                            'Credito': recebimento_venda.contaCredito
                    }
                    )
                    logging.warning(recebimentos)

                listarVendasTemplate.append(
                    {
                     'idVenda': venda.identificadorVenda,
                     'cliente': venda.cliente,
                     'dataVenda': venda.criados,
                     'valorVenda': valorVendaTotal,
                     'recebimentos': recebimentos,
                     }
                )
                recebimentos = []
                logging.warning(type(listarVendasTemplate))
                valorVendaTotal = 0
                identificadorVenda = venda.identificadorVenda
        context['listarVendas'] = listarVendasTemplate
        return(context)

class ParcelasReceberModalView(TemplateView):

    template_name = 'parcelasarecebermodal.html'
    def get_context_data(self, **kwargs):

        context = super(ParcelasReceberModalView, self).get_context_data(**kwargs)
        context['mensagem'] = ''

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

        contasDetalhadas = Conta.objects.all()
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
        conta_recebimento = Conta.objects.get(id=self.request.POST.get('contaCredito'), ativo=True)
        conta_cartao = Cartao.objects.get(cartao=conta_recebimento.cartao)
        taxa = 0
        if conta_recebimento.categoria_id == 1:
            logging.warning("Cartão de crédito")
            logging.warning(f'Parcelas do Cartão:{self.request.POST.get("parcelaCartao")}')
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
        elif conta_recebimento.categoria_id == 2:
            logging.warning("Depósito em real")
        elif conta_recebimento.categoria_id == 3:
            logging.warning("Espécie")
        valor_recebimento = (1-taxa/100) * float(self.request.POST.get('valorRecebido'))

        dataform = MovimentacaoConta(contaCredito_id=self.request.POST.get('contaCredito'),
                                     criados=hoje,
                                     contaDebito="0",
                                     valorCredito=valor_recebimento,
                                     identificadorVenda=self.request.POST.get('identificadorVenda'),
                                     descricao=self.request.POST.get('descricao'),
                                     identificadorDolar=False,
        )
        dataform.save()
        context['mensagem'] = "Recebimento Efetuado"
        return super(TemplateView, self).render_to_response(context)
