from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from Compras.models import Fornecedor, LocalizacaoCompra
from Vendas.models import Cliente
from datetime import date, datetime
import re
import logging


# Create your views here.
class CadastroClienteView(TemplateView):
    template_name = "cadastrocliente.html"

    def get_context_data(self, **kwargs):
        context = super(CadastroClienteView, self).get_context_data(**kwargs)
        if self.request.GET.__contains__("id_cliente"):
            if self.request.GET["funcao"] == "apagar":
                apagar_cliente = Cliente(id=self.request.GET["id_cliente"])
                apagar_cliente.delete()
        if self.request.GET.__contains__("cliente_cadastrado"):
            logging.warning("Cliente cadastrado")
            context['cliente_cadastrado'] = 1
        clientes_cadastrados = Cliente.objects.all().order_by('-criados')
        clientesTemplate = []
        for cliente_cadastrado in clientes_cadastrados:
            clientesTemplate.append(
                {
                    "data": cliente_cadastrado.criados,
                    "nome_cliente": cliente_cadastrado.nomeCliente,
                    "id_cliente": cliente_cadastrado.id,
                }
            )
        context['clientes'] = clientesTemplate;
        return context

    def post(self, request, *args, **kwargs):
        context = super(CadastroClienteView, self).get_context_data(**kwargs)
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        dataform_cliente = Cliente(
            nomeCliente=self.request.POST.get("nomecliente"),
            criados=hoje,
            ativo="True",
        )
        dataform_cliente.save()
        context['mensagem'] = 'Cadastrado'
        return HttpResponseRedirect('/cadastrocliente/?cliente_cadastrado=1', context)
        #return super(TemplateView, self).render_to_response(context)

class CadastroFornecedorView(TemplateView):
    template_name = "cadastrofornecedor.html"

    def get_context_data(self, **kwargs):
        context = super(CadastroFornecedorView, self).get_context_data(**kwargs)
        if self.request.GET.__contains__("id_fornecedor"):
            if self.request.GET["funcao"] == "apagar":
                apagar_fornecedor = Fornecedor(id=self.request.GET["id_fornecedor"])
                apagar_fornecedor.delete()
        if self.request.GET.__contains__("fornecedor_cadastrado"):
            logging.warning("Fornecedor cadastrado")
            context['fornecedor_cadastrado'] = 1
        fornecedores_cadastrados = Fornecedor.objects.all().order_by('-criados')
        fornecedoresTemplate = []
        for fornecedor_cadastrado in fornecedores_cadastrados:
            logging.warning(fornecedor_cadastrado.criados)
            logging.warning(fornecedor_cadastrado.nomeFornecedor)
            logging.warning(fornecedor_cadastrado.id)
            fornecedoresTemplate.append(
                {
                    "data": fornecedor_cadastrado.criados,
                    "nome_fornecedor": fornecedor_cadastrado.nomeFornecedor,
                    "id_fornecedor": fornecedor_cadastrado.id,
                }
            )
        context['mensagem'] = ""
        context['fornecedores'] = fornecedoresTemplate;
        context['localidade'] = LocalizacaoCompra.objects.all()
        context['mensagem'] = ""
        return context

    def post(self, request, *args, **kwargs):
        context = super(CadastroFornecedorView, self).get_context_data(**kwargs)
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        dataform_fornecedor = Fornecedor(
            nomeFornecedor=self.request.POST.get("nomefornecedor"),
            localizacaoCompra_id=self.request.POST.get("localidade"),
            criados=hoje,
            ativo="True",
        )
        dataform_fornecedor.save()
        return HttpResponseRedirect('/cadastrofornecedor/?fornecedor_cadastrado=1', context)
        #return super(TemplateView, self).render_to_response(context)

class CadastroLocalizacaoView(TemplateView):
    template_name = "cadastrolocalizacao.html"

    def get_context_data(self, **kwargs):
        context = super(CadastroLocalizacaoView, self).get_context_data(**kwargs)
        if self.request.GET.__contains__("id_localidade"):
            if self.request.GET["funcao"] == "apagar":
                apagar_cliente = LocalizacaoCompra(id=self.request.GET["id_localidade"])
                apagar_cliente.delete()
        if self.request.GET.__contains__("localizacao_cadastrada"):
            logging.warning("Localizacao cadastrada")
            context['localizacao_cadastrada'] = 1
        localidades_cadastradas = LocalizacaoCompra.objects.all().order_by('-criados')
        localidadesTemplate = []
        for localidade_cadastrada in localidades_cadastradas:
            localidadesTemplate.append(
                {
                    "data": localidade_cadastrada.criados,
                    "nome_localidade": localidade_cadastrada.localizacaoCompra,
                    "id_localidade": localidade_cadastrada.id,
                }
            )
        context['mensagem'] = ""
        context['localidades'] = localidadesTemplate;
        return context

    def post(self, request, *args, **kwargs):
        context = super(CadastroLocalizacaoView, self).get_context_data(**kwargs)
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        dataform_localidade = LocalizacaoCompra(
            localizacaoCompra=self.request.POST.get("nome_localidade"),
            criados=hoje,
            ativo="True",
        )
        dataform_localidade.save()

        return HttpResponseRedirect('/cadastrolocalizacao/?localizacao_cadastrada=1', context)
