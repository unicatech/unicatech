from django.urls import path
from .views import CadastroFornecedorView, CadastroClienteView

urlpatterns = [
    path('cadastrofornecedor/', CadastroFornecedorView.as_view(), name='cadastrofornecedor'),
    path('cadastrocliente/', CadastroClienteView.as_view(), name='cadastrocliente'),
]
