from django.contrib import admin
from .models import Procedimentos, Exames, Especialidades, DadosMedico, DatasAbertas

# Register your models here.
admin.site.register(Especialidades)
admin.site.register(Procedimentos)
admin.site.register(Exames)
admin.site.register(DadosMedico)
admin.site.register(DatasAbertas)
