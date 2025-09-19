from django.urls import path
from . import views

urlpatterns = [
    path('cadastro_medico/', views.fnctn_cdstr_medico, name="url_cdstr_medico"),
    path('abrir_horario/', views.fnctn_open_horario, name="url_open_horario"),
    path('consultas_medico/', views.fnctn_cnslts_medico, name="url_cnslts_medico"),
    path('consulta_area_medico/<int:id_consulta>/', views.fnct_cnslta_area_mdco, name="url_cnslta_area_mdco"),
    path('finalizar_consulta/<int:id_consulta>/', views.fnct_fnlzar_cnslta, name="url_fnlzar_cnslta"),
    path('add_documento/<int:id_consulta>/', views.fnctn_add_dcmnto, name="url_add_dcmnto"),
    path('add_notfcacao/<int:id_consulta>/', views.fnctn_add_notfcacao, name="url_add_notfcacao"),
    path('especialidades_medica/', views.fnct_espclddes_mdca, name="url_espclddes_mdca"),
    path('cadastro_especialidade/<int:id_espcldde>/', views.fnct_espclddes_cdstro, name="url_espclddes_cdstro"),
]