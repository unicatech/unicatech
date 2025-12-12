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
        alertas_novos = 0
        for alerta in alertas:
            if alerta.novo == 1:
                alertas_novos = alertas_novos + 1
            alertas_template.append({
                'alerta': alerta.evento,
                'novidade': alerta.novo,
            })
            alerta.novo = 0
            alerta.save()
        request.alertas = alertas
        request.novidades = alertas_novos

        response = self.get_response(request)

        # Executa DEPOIS da view (opcional)
        #print("Resposta enviada")

        return response