from django.contrib import admin
from .models import Doador, Hemocentro, Agendamento


admin.site.register(Doador)
admin.site.register(Hemocentro)
admin.site.register(Agendamento)