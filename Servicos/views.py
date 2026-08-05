from django.db.models import Model
from django.shortcuts import render
from django.views.generic import TemplateView
from core.models import Alertas
import re
import logging
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect

from Servicos.models import Servico
from Vendas.models import Cliente, Venda
from Produtos.models import Produto
from core.models import Alertas
from Contas.models import MovimentacaoConta, Conta, Cartao, RecebimentoCartao
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.
class ListarServicosView(TemplateView):
    template_name = 'listarservicos.html'

    def get(self, request, *args, **kwargs):
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")

        if request.GET.get("funcao") == "finalizar":
            servico = Servico.objects.get(
                identificador_servico=request.GET["identificador_servico"]
            )
            if servico.imei == "0":
               context = self.get_context_data(**kwargs)
               return render(request, "abrirservico.html", context)
            else:
                evento_servico = f"Finalização de serviço feita por {request.user.first_name} na Ordem de Serviço número {request.GET['identificador_servico']}"
                alerta = Alertas(
                    criados=str(hoje),
                    evento=evento_servico,
                    usuario_id=request.user.id,
                    identificador_servico=request.GET["identificador_servico"],
                    icone="tools.svg"
                )
                alerta.save()

        if request.GET.get("funcao")  == "reabrir":
            evento_servico = f"Reabertura de serviço feita por {request.user.first_name} na Ordem de Serviço número {request.GET['identificador_servico']}"
            alerta = Alertas(
                criados=str(hoje),
                evento=evento_servico,
                usuario_id=request.user.id,
                identificador_servico=request.GET["identificador_servico"],
                icone="tools.svg"
            )
            alerta.save()

        if request.GET.get("funcao")  == "apagar":
            if self.request.GET.__contains__("identificador_servico"):
                evento_servico = f"Ordem de Serviço apagada por {request.user.first_name} na Ordem de Serviço número {request.GET['identificador_servico']}"
                alerta = Alertas(
                    criados=str(hoje),
                    evento=evento_servico,
                    usuario_id=request.user.id,
                    identificador_servico=request.GET["identificador_servico"],
                    icone="tools.svg"
                )
                alerta.save()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListarServicosView, self).get_context_data(**kwargs)

        if self.request.GET.__contains__("identificador_servico"):
            vendas_servico = Venda.objects.filter(ativo=True, identificador_servico=self.request.GET["identificador_servico"])
            eventos_servico = Alertas.objects.filter(ativo=True, identificador_servico=self.request.GET["identificador_servico"])
            listar_produtos_template = []
            eventos = []
            context['sem_produtos'] = 1
            for venda in vendas_servico:
                listar_produtos_template.append(
                    {
                     'idProduto': venda.produto_id,
                     'nome_produto': venda.produto.NomeProduto,
                     'quantidade_produto': venda.quantidadeProduto,
                     'id_tabela_venda': venda.id,
                     'identificador_servico': venda.identificador_servico,
                     'tecnico': venda.usuario.first_name,
                     'descricao_venda': venda.descricao,
                     }
                )
                context['sem_produtos'] = 0

            for evento in eventos_servico:
                eventos.append(
                    {
                        'identificador_servico': evento.identificador_servico,
                        'evento': evento.evento,
                        'tecnico': evento.usuario.first_name,
                        'data': evento.criados,
                    }
                )

            servico = Servico.objects.get(identificador_servico=self.request.GET["identificador_servico"])
            context['produtos_servico_identificado'] = listar_produtos_template
            context['eventos'] = eventos
            context['identificador_servico'] = servico.identificador_servico
            context['descricao'] = servico.descricao
            context['imei'] = servico.imei
            context['data_criado'] = servico.criados
            context['cliente'] = servico.cliente.nomeCliente

            if self.request.GET["funcao"] == "finalizar":
                servico_interno = Servico.objects.get(identificador_servico=self.request.GET["identificador_servico"])
                if servico_interno.imei != "0":
                    Servico.objects.filter(identificador_servico=self.request.GET["identificador_servico"]).update(ativo=False)
                else:
                    context['data_servico'] = servico_interno.criados.strftime('%d-%m-%Y')
                    context['cliente'] = servico_interno.cliente.nomeCliente
                    context['imei'] = servico_interno.imei
                    context['descricao'] = servico_interno.descricao
                    context['identificador_servico'] = self.request.GET["identificador_servico"]
                    context['idCliente'] = servico_interno.cliente_id
                    context['botaosubmit'] = "Atualizar Ordem de Serviço"
                    context['clientes'] = Cliente.objects.filter().order_by('nomeCliente')

            if self.request.GET["funcao"] == "reabrir":
                Servico.objects.filter(identificador_servico=servico.identificador_servico).update(ativo=True)

            if self.request.GET["funcao"] == "apagar":
                if self.request.GET.__contains__("identificador_servico"):
                    estorno_estoque_produtos = Venda.objects.filter(identificador_servico=self.request.GET["identificador_servico"],ativo=True)
                    for estoque in estorno_estoque_produtos:
                        atualizar_estoque = Produto.objects.get(id=estoque.produto_id)
                        atualizar_estoque.estoque = atualizar_estoque.estoque + estoque.quantidadeProduto
                        atualizar_estoque.save()
                        Venda.objects.filter(id=estoque.id).update(ativo=False)
                    Servico.objects.filter(identificador_servico=self.request.GET["identificador_servico"]).delete()

            if self.request.GET["funcao"] == "apagarprodutoservico":
                if self.request.GET.__contains__("id_tabela_venda"):
                    quantidade_produto_venda = Venda.objects.get(id=self.request.GET["id_tabela_venda"],ativo=True)
                    atualizar_estoque = Produto.objects.get(id=quantidade_produto_venda.produto_id)
                    atualizar_estoque.estoque = atualizar_estoque.estoque + quantidade_produto_venda.quantidadeProduto
                    atualizar_estoque.save()
                    Venda.objects.filter(id=self.request.GET["id_tabela_venda"]).update(ativo=False)


        hoje = timezone.now().date()
        seis_meses_atras = hoje - timedelta(days=180)
        if self.request.resolver_match.url_name == "servicoemaberto":
            servicos = Servico.objects.filter(ativo=True, criados__gte=seis_meses_atras).order_by(
                '-identificador_servico')
        if self.request.resolver_match.url_name == "listarservicos":
            servicos = Servico.objects.filter(ativo=False, criados__gte=seis_meses_atras).order_by(
                '-identificador_servico')

        listar_servicos_template = []
        identificador_servico = 0

        for servico in servicos:
            if identificador_servico != servico.identificador_servico:
                servico_identificado = Servico.objects.filter(identificador_servico=servico.identificador_servico,ativo=True).order_by('-identificador_servico')
                valor_servico_total = 0
                for servico in servico_identificado:
                    valor_servico_total = valor_servico_total + servico.preco_servico

                listar_servicos_template.append(
                    {
                        'identificador_servico': servico.identificador_servico,
                        'cliente': servico.cliente.nomeCliente,
                        'id_cliente': servico.cliente.id,
                        'tecnico': servico.usuario.first_name,
                        'data_servico': servico.criados,
                        'valor_servico': servico.preco_servico,
                        'imei': servico.imei,
                        'descricao': servico.descricao,
                     }
                )
                identificador_servico = servico.identificador_servico

        context['listar_servicos'] = listar_servicos_template

        return(context)

    def get_template_names(self):
        if self.request.GET.get("funcao") == "modalvenda":
            return ["fazervendasservicomodal.html"]
        if self.request.GET.get("funcao") == "modalvisualizar":
            return ["detalhesservicomodal.html"]
        if self.request.resolver_match.url_name == "servicoemaberto":
            return ["servicoemaberto.html"]
        if self.request.resolver_match.url_name == "listarservicos":
            return ["listarservicos.html"]
        return [self.template_name]

    def post(self, request, *args, **kwargs):
        context = super(ListarServicosView, self).get_context_data(**kwargs)
        data_inicio = self.request.POST.getlist('data_inicio')
        data_fim = self.request.POST.getlist('data_fim')
        imei = self.request.POST.get('imei')

        servicos = Servico.objects.order_by('-identificador_servico')
        if data_inicio[0] and data_fim[0]:
            data_inicio = datetime.strptime(data_inicio[0], '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim[0], '%Y-%m-%d').date()
            servicos = servicos.filter(
                criados__range=[data_inicio, data_fim]
            )
        if imei:
            servicos = servicos.filter(imei__icontains=imei)

        listar_servicos_template = []
        identificador_servico = 0

        for servico in servicos:
            if identificador_servico != servico.identificador_servico:
                servico_identificado = Servico.objects.filter(identificador_servico=servico.identificador_servico,ativo=True).order_by('-identificador_servico')
                valor_servico_total = 0
                for servico in servico_identificado:
                    valor_servico_total = valor_servico_total + servico.preco_servico

                listar_servicos_template.append(
                    {
                        'identificador_servico': servico.identificador_servico,
                        'cliente': servico.cliente.nomeCliente,
                        'id_cliente': servico.cliente.id,
                        'tecnico': servico.usuario.first_name,
                        'data_servico': servico.criados,
                        'valor_servico': servico.preco_servico,
                        'imei': servico.imei,
                        'descricao': servico.descricao,
                     }
                )
                identificador_servico = servico.identificador_servico

        context['listar_servicos'] = listar_servicos_template
        return render(request, 'listarservicosbusca.html', context)



class AbrirServicoView(TemplateView):
    template_name = 'abrirservico.html'

    def get_context_data(self, **kwargs):
        context = super(AbrirServicoView, self).get_context_data(**kwargs)
        context['botaosubmit'] = "Abrir Ordem de Serviço"
        agora = datetime.now()
        context['data_servico'] = agora.strftime("%d-%m-%Y")
        if self.request.GET.__contains__("cliente_sem_cadastro"):
            context['cliente_sem_cadastro'] = 1

        #Popular template
        if self.request.GET.__contains__("identificador_servico"):
            servico_editar = Servico.objects.get(identificador_servico=self.request.GET["identificador_servico"])
            context['data_servico'] = servico_editar.criados.strftime('%d-%m-%Y')
            context['imei'] = servico_editar.imei
            context['descricao'] = servico_editar.descricao
            context['identificador_servico'] = self.request.GET["identificador_servico"]
            context['idCliente'] = servico_editar.cliente_id
            context['botaosubmit'] = "Atualizar Ordem de Serviço"

        context['clientes'] = Cliente.objects.filter().order_by('nomeCliente')
        return context

    def post(self, request, *args, **kwargs):
        context = super(AbrirServicoView, self).get_context_data(**kwargs)

        cliente = self.request.POST.getlist('cliente')
        data_servico = self.request.POST.getlist('data_servico')
        imei = self.request.POST.getlist('imei')
        descricao = self.request.POST.getlist('descricao')
        cliente_banco = Cliente.objects.get(id=cliente[0],ativo=True)
        data_servico_modificada = re.sub(r'(\d{1,2})-(\d{1,2})-(\d{4})', '\\3-\\2-\\1', data_servico[0])

        if self.request.POST.__contains__("identificador_servico"):
            identificador_servico = self.request.POST.getlist('identificador_servico')
            if identificador_servico[0] != "":
                Servico.objects.get(identificador_servico=identificador_servico[0]).delete()
                proximo_servico = identificador_servico[0]
                evento_servico = f"Ordem de Serviço número {proximo_servico} editada por {request.user.first_name} para o cliente {cliente_banco.nomeCliente}."
                alerta = Alertas(
                    criados=str(data_servico_modificada),
                    evento=evento_servico,
                    identificador_servico=str(proximo_servico),
                    usuario_id=request.user.id,
                    icone="tools.svg"
                )
                alerta.save()
            else:
                try:
                    ultimo_servico = Servico.objects.order_by('-identificador_servico')
                    identificador_servico = 0
                    for identificador in ultimo_servico:
                        identificador_servico = identificador.identificador_servico
                        break
                    proximo_servico = identificador_servico + 1
                except:
                    proximo_servico = 1

                evento_servico = f"Ordem de Serviço número {proximo_servico} aberta por {request.user.first_name} para o cliente {cliente_banco.nomeCliente}."
                alerta = Alertas(
                    criados=str(data_servico_modificada),
                    evento=evento_servico,
                    identificador_servico=str(proximo_servico),
                    usuario_id=request.user.id,
                    icone="tools.svg"
                )
                alerta.save()

        if cliente[0] == "":
            return HttpResponseRedirect('/' + tipo_produto[0] + '/?cliente_sem_cadastro=1', context)

        logging.warning(data_servico_modificada)
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

        return HttpResponseRedirect("/servicoemaberto/?abrirservico=1")

