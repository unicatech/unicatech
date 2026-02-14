from core.models import Alertas
from django.shortcuts import redirect
from django.conf import settings
import logging

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not request.user.is_authenticated
            and not request.path.startswith(settings.LOGIN_URL)
            and not request.path.startswith('/admin/')
            and not request.path.startswith('/static/')
        ):
            return redirect(settings.LOGIN_URL)

        response = self.get_response(request)
        return response

class MostrarAlertas:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Executa ANTES da view
        alertas = Alertas.objects.all().order_by('-id')[:10]
        alertas_template=[]
        alertas_novos = 0

        user = request.user
        if user.is_authenticated:
            for alerta in alertas:
                # Se o usuário ainda não viu
                if not alerta.usuarios_vistos.filter(id=user.id).exists():
                    alertas_novos += 1

                alertas_template.append({
                    'evento': alerta.evento,
                    'novo': not alerta.usuarios_vistos.filter(id=user.id).exists(),
                    'data': alerta.criados,
                    'icone': alerta.icone,
                })

                # Marcar como visto
                alerta.usuarios_vistos.add(user)

        request.alertas = alertas_template
        request.novidades = alertas_novos
        response = self.get_response(request)

        # Executa DEPOIS da view (opcional)
        return response