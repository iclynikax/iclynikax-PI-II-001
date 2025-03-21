from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name="url_home"),
    path('escolher_horario/<int:id_dados_medicos>/', views.fnctn_esclhr_hrrio, name="url_escler_hrrio"),
    path('agendar_horario/<int:id_data_aberta>/', views.fnctn_agndr_hrrio, name="url_agndr_horario"),
    path('minhas_consultas/', views.fnctn_mnhs_cnslts, name="url_mnhs_cnslts"),
    path('consulta/<int:id_consulta>/', views.fnctn_cnslta, name="url_cnslta"),
]