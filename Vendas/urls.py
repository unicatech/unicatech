from django.urls import path
from .views import ListarVendasView, ParcelasReceberView, ParcelasReceberModalView, FazerVendasView

urlpatterns = [
    path('fazervendas/', FazerVendasView.as_view(), name='fazervendas'),
    path('listarvendas/', ListarVendasView.as_view(), name='listarvendas'),
    path('parcelasareceber/', ParcelasReceberView.as_view(), name='parcelasareceber'),
    path('parcelasarecebermodal/', ParcelasReceberModalView.as_view(), name='parcelasarecebermodal'),

]
