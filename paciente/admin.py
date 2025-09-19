from django.contrib import admin
from .models import Consulta, Documento, Notificacao, Pet, Pet_Cliente

# Register your models here.
admin.site.register(Pet)
admin.site.register(Pet_Cliente)
admin.site.register(Consulta)
admin.site.register(Documento)
admin.site.register(Notificacao)
