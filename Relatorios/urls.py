from django.urls import path
from .views import *


urlpatterns = [
    path('relatorioproduto/', RelatorioProdutoView.as_view(), name='relatorioproduto'),
    #path('relatoriorecebimentosconta/', RelatorioRecebimentosContaView.as_view(), name='relatoriorecebimentosconta'),
    #path('relatoriorecebimentosproduto/', RelatorioRecebimentosProdutoView.as_view(), name='relatoriorecebimentosproduto'),

]
