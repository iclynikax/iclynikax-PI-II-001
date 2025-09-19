from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name="url_home"),
    path('escolher_horario/<int:id_dados_medicos>/', views.fnctn_esclhr_hrrio, name="url_escler_hrrio"),
    path('agendar_horario/<int:id_data_aberta>/', views.fnctn_agndr_hrrio, name="url_agndr_horario"),
    path('minhas_consultas/', views.fnctn_mnhs_cnslts, name="url_mnhs_cnslts"),
    path('consulta/<int:id_consulta>/', views.fnctn_cnslta, name="url_cnslta"),
    path('consultas/', views.fnctn_pcnts_cnsltas, name="url_pcnts_cnsltas"),
    path('pet_cliente_cadastro/<int:id_PetCliente>/', views.fnctn_pet_clnte_cdstro, name="url_pet_clnte_cdstro"),
    path('exames/', views.fnctn_pcnts_exmes, name="url_pcnts_exmes"),
    path('minhas_autoriza/', views.fnctn_mnhs_atrza, name="url_mnhs_atrza"),
    path('autorizacoes/', views.fnctn_atrzacoes, name="url_atrzacoes"),
    path('autorizacao/<int:id_Ntfccao>/<int:id_consulta>/', views.fnctn_atrzacao, name="url_atrzacao"),
    path('salvar_notificacao/', views.fnctn_slvr_ntfccao, name='url_salvar_notificacao'),
    path('atualizaautorizacao/<int:id_Ntfccao>/<int:id_consulta>/', views.fnctn_atlza_atrzacao, name="url_atlza_atrzacao"),
    path('add_autorizacao/<int:id_consulta>/', views.fnctn_add_atrzacao, name="url_add_atrzacao"),
    path('envia_whtsapp_ntficacao/<int:id_Ntfccao>/', views.fnctn_envia_whtsapp_ntficacao, name="url_envia_whtsapp_ntficacao"),
    path('envia_email_ntficacao/<int:id_Ntfccao>/', views.fnctn_envia_email_ntficacao, name="url_envia_email_ntficacao"),
    path('atrzcao_rspsta/', views.fnctn_atrzcao_rspsta, name="url_atrzcao_rspsta"),

    
]