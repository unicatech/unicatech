from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import Produto, CategoriaProduto

from Vendas.models import Venda

from datetime import date, datetime
import re
import logging

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
        agora = datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        dataform = Produto(
            criados=hoje,
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
        context['categoriaprodutoselecionado'] = CategoriaProduto.objects.get(
            categoria=context['produtoselecionado'].categoria)
        context['mensagem'] = ''
        return context

    def post(self, request, *args, **kwargs):
        dataform = Produto.objects.get(id=self.request.POST.get('idProduto'))
        dataform.NomeProduto = self.request.POST.get('nomeproduto')
        dataform.categoria_id = self.request.POST.get('categoria')
        dataform.SKU = self.request.POST.get('SKU')
        dataform.estoque = self.request.POST.get('estoque')
        dataform.save()
        context = super(EditProductView, self).get_context_data(**kwargs)
        context['produtos'] = Produto.objects.all()
        context['categoriaproduto'] = CategoriaProduto.objects.all()
        return HttpResponseRedirect('/productlist/?produtocadastrado=1')

