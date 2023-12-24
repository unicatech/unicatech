from django.urls import path
from .views import FazerComprasView, ListarComprasView, LocalizacaoCompraView

urlpatterns = [
    path('fazercompras/', FazerComprasView.as_view(), name='fazercompras'),
    path('listarcompras/', ListarComprasView.as_view(), name='listarcompras'),
    path('localizacaocompra/', LocalizacaoCompraView.as_view(), name='localizacaocompra'),
]
