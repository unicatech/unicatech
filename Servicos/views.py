from django.db.models import Model
from django.shortcuts import render
from django.views.generic import TemplateView
from core.models import Alertas
import re
import logging
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import date, datetime, timedelta

from Servicos.models import Servico
from Vendas.models import Cliente
from core.models import Alertas
from Contas.models import MovimentacaoConta, Conta, Cartao, RecebimentoCartao

# Create your views here.
class ListarServicosView(TemplateView):
    template_name = 'listarservicos.html'

    def get_context_data(self, **kwargs):
        context = super(ListarServicosView, self).get_context_data(**kwargs)

        if self.request.GET.__contains__("id_servico"):
            if self.request.GET["funcao"] == "apagar":
                pass
            #para implementar apagar servico checando todos os componentes utilizados no servico e garantir
            #que sejam removidos

        hoje = timezone.now().date()
        seis_meses_atras = hoje - timedelta(days=180)
        servicos = Servico.objects.filter(ativo=True, criados__gte=seis_meses_atras).order_by('-identificador_servico')
        listar_servicos_template = []
        identificador_servico = 0

        for servico in servicos:
            if identificador_servico != servico.identificador_servico:
                servico_identificado = Servico.objects.filter(identificador_servico=servico.identificador_servico,ativo=True).order_by('-identificador_servico')
                valor_servico_total = 0
                for servico in servico_identificado:
                    valor_servico_total = valor_servico_total + servico.preco_servico

                #Implementar os recebimentos
                #recebimentos_servico = MovimentacaoConta.objects.filter(
                #    identificador_servico=venda.identificadorVenda,
                #    identificadorCompra=0,
                #    ativo=True)
                #for recebimento_servico in recebimentos_servico:
                #    recebimentos.append({
                #            'valor_recebimento': recebimento_servico.valorCredito,
                #            'data': recebimento_servico.criados,
                #            'Credito': recebimento_servico.contaCredito,
                #            'identificador_parcela': recebimento_servico.id,
                #    })
                #    valor_recebido_servico = valor_recebido_servico + recebimento_servico.valorCredito

                #total_a_receber = valor_servico_total - valor_recebido_servico
                listar_servicos_template.append(
                    {
                        'id_servico': servico.identificador_servico,
                        'cliente': servico.cliente.nomeCliente,
                        'id_cliente': servico.cliente.id,
                        'tecnico': servico.usuario.first_name,
                        'data_servico': servico.criados,
                        'valor_servico': servico.preco_servico,
                        'imei': servico.imei,
                        #'recebimentos': recebimentos,
                        #'total_a_receber': total_a_receber,
                     }
                )
                logging.warning("Id Cliente")
                logging.warning(servico.cliente.id)
                identificador_servico = servico.identificador_servico

        context['listar_servicos'] = listar_servicos_template
        return(context)

    def get_template_names(self):
        if self.request.GET.get("funcao") == "modalvenda":
            logging.warning("Entrei modal servico")
            return ["fazervendasservicomodal.html"]
        return [self.template_name]


class AbrirServicoView(TemplateView):
    template_name = 'abrirservico.html'

    def get_context_data(self, **kwargs):
        context = super(AbrirServicoView, self).get_context_data(**kwargs)
        if self.request.GET.__contains__("cliente_sem_cadastro"):
            context['cliente_sem_cadastro'] = 1

        #Popular template
        context['clientes'] = Cliente.objects.filter().order_by('nomeCliente')
        return context

    def post(self, request, *args, **kwargs):
        context = super(AbrirServicoView, self).get_context_data(**kwargs)

        try:
            ultimo_servico = Servico.objects.order_by('-identificador_servico')
            id_servico = 0
            for identificador in ultimo_servico:
                id_servico = identificador.identificador_servico
                logging.warning(id_servico)
                break
            proximo_servico = id_servico + 1
        except:
            proximo_servico = 1

        cliente = self.request.POST.getlist('cliente')
        data_servico = self.request.POST.getlist('data_servico')
        imei = self.request.POST.getlist('imei')
        descricao = self.request.POST.getlist('descricao')

        data_servico_modificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', data_servico[0])

        if cliente[0] == "":
            return HttpResponseRedirect('/' + tipo_produto[0] + '/?cliente_sem_cadastro=1', context)

        # Cadastrando Servico
        form_servico = Servico(
            criados=str(data_servico_modificada),
            identificador_servico=str(proximo_servico),
            cliente_id=cliente[0],
            descricao=descricao[0],
            imei=imei[0],
            usuario=request.user,
            ativo=True,
        )
        form_servico.save()

        cliente = Cliente.objects.get(id=cliente[0],ativo=True)
        evento_servico = f"Ordem de Serviço aberta por {request.user.first_name} para o cliente {cliente.nomeCliente}."
        alerta = Alertas(
            criados=str(data_servico_modificada),
            evento=evento_servico,
            usuario_id=request.user.id,
            icone="sale.svg"
        )
        alerta.save()

        return HttpResponseRedirect("/listarservicos/?abrirservico=1")