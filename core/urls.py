from django.urls import path
from .views import IndexView, ProductListView, AddProductView, EditProductView, ListarContaView, CriarContaView, ComprarDolarView, AdicionarFundosView, EditarContaView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('productlist/', ProductListView.as_view(), name='productlist'),
    path('addproduct/', AddProductView.as_view(), name='addproduct'),
    path('editproduct/', EditProductView.as_view(), name='editproduct'),
    path('listarconta/', ListarContaView.as_view(), name='listarconta'),
    path('criarconta/', CriarContaView.as_view(), name='criarconta'),
    path('editarconta/', EditarContaView.as_view(), name='editarconta'),
    path('comprardolar/', ComprarDolarView.as_view(), name='comprardolar'),
    path('adicionarfundos/', AdicionarFundosView.as_view(), name='adicionarfundos'),
]
