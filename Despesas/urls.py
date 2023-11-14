from django.urls import path
from .views import AdicionarDespesa

urlpatterns = [
    path('adicionardespesa/', AdicionarDespesa.as_view(), name='adicionardespesa'),
]
