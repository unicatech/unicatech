from django.urls import path
from .views import AdicionarDespesa, DespesasPeriodicas

urlpatterns = [
    path('adicionardespesa/', AdicionarDespesa.as_view(), name='adicionardespesa'),
    path('despesasperiodicas/', DespesasPeriodicas.as_view(), name='despesasperiodicas'),
]
