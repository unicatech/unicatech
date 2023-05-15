from django.urls import path
from .views import ListarContaView, CriarContaView, ComprarDolarView, AdicionarFundosView, EditarContaView

urlpatterns = [
    path('listarconta/', ListarContaView.as_view(), name='listarconta'),
    path('criarconta/', CriarContaView.as_view(), name='criarconta'),
    path('editarconta/', EditarContaView.as_view(), name='editarconta'),
    path('comprardolar/', ComprarDolarView.as_view(), name='comprardolar'),
    path('adicionarfundos/', AdicionarFundosView.as_view(), name='adicionarfundos'),
]
