from django.urls import path
from .views import FazerComprasView, ListarComprasView, LocalizacaoCompraView

urlpatterns = [
    path('fazercompras/', FazerComprasView.as_view(), name='fazercompras'),
    path('fazercomprasaparelhos/', FazerComprasView.as_view(), name='fazercomprasaparelhos'),
    path('fazercompraspecas/', FazerComprasView.as_view(), name='fazercompraspecas'),
    path('listarcompras/', ListarComprasView.as_view(), name='listarcompras'),
    path('localizacaocompra/', LocalizacaoCompraView.as_view(), name='localizacaocompra'),
]
