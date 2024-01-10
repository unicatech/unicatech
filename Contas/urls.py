from django.urls import path
from .views import ListarContaView, CriarContaView, ComprarDolarView, AdicionarFundosView, EditarContaView, RetiradaView, ListarMovimentacoesView

urlpatterns = [
    path('listarconta/', ListarContaView.as_view(), name='listarconta'),
    path('listarmovimentacoes/', ListarMovimentacoesView.as_view(), name='listarmovimentacoes'),
    path('criarconta/', CriarContaView.as_view(), name='criarconta'),
    path('editarconta/', EditarContaView.as_view(), name='editarconta'),
    path('comprardolar/', ComprarDolarView.as_view(), name='comprardolar'),
    path('adicionarfundos/', AdicionarFundosView.as_view(), name='adicionarfundos'),
    path('retirada/', RetiradaView.as_view(), name='retirada'),
]
