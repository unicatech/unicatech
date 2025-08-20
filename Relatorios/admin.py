from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Dummy

@admin.register(Dummy)
class DummyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Faz o app aparecer no menu
        return True

    def has_view_permission(self, request, obj=None):
        # Impede erro de acesso à lista (porque não há dados)
        return False
