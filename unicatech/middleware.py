from core.models import Alertas
import logging

class MostrarAlertas:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Executa ANTES da view
        #logging.warning("Requisição recebida:", request.path)
        #logging.warning("Alimentando Alertas")

        alertas = Alertas.objects.all().order_by('-id')[:10]
        alertas_template=[]
        for alerta in alertas:
            alertas_template.append({
                'alerta': alerta.evento,
            })
        request.alertas=alertas

        response = self.get_response(request)

        # Executa DEPOIS da view (opcional)
        #print("Resposta enviada")

        return response