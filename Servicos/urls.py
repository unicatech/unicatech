from django.urls import path
from .views import *


urlpatterns = [
    path('listarservicos/', ListarServicosView.as_view(), name='listarservicos'),
    path('servicoemaberto/', ListarServicosView.as_view(), name='servicoemaberto'),
    path('abrirservico/', AbrirServicoView.as_view(), name='abrirservico'),
]
