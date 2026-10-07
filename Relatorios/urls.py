from django.urls import path
from .views import *


urlpatterns = [
    path('relatorioproduto/', RelatorioProdutoView.as_view(), name='relatorioproduto'),
    path('relatoriorecebimentosconta/', RelatorioRecebimentosContasView.as_view(), name='relatoriorecebimentosconta'),
    path('relatoriorecebimentoprodutos/', RelatorioRecebimentoProdutosView.as_view(), name='relatoriorecebimentoprodutos'),
    path('relatorioeventos/', RelatorioEventosView.as_view(), name='relatorioeventos'),
    path('relatoriofaturamentoelucro/', RelatorioFaturamentoeLucroView.as_view(), name='relatoriofaturamentoelucro'),
    path('relatorioservicostecnico/', RelatorioServicosTecnicoView.as_view(), name='relatorioservicostecnico'),
    path('relatoriolucrovendas/', RelatorioLucroVendasView.as_view(), name='relatoriolucrovendas'),
]
