from django.urls import path
from . import views


urlpatterns = [
    path('cadastro/', views.fnct_cdstro, name="url_cadastro"),
    path('lista/', views.fnct_clnts_lista, name="url_clnts_lista"),
    path('cliente/<int:id_cliente>/',
         views.fnct_clnts_edit, name="url_clnts_edit"),

    path('buscar-endereco/<str:cep>/',
         views.buscar_endereco, name='buscar_endereco'),
    path('edita-endereco/<int:id_endrco>/',
         views.fnct_endr_clnt_prfl, name='url_ender_clnte_prfl'),
    path('edita-endereco/<int:id_endrco>/',
         views.fnct_endereco_clnte_cdstro, name='url_endereco_clnte_cdstro'),
    path('cliente-endereco-add/<int:id_cliente>/',
         views.fnct_endereco_clnte_add, name='url_endereco_clnte_add'),




    path('cliente_PI_I/<int:id_cliente>/',
         views.fnct_clnts_edit_PI_I, name="url_clnts_edit_PI_I"),
    path('login/', views.fnct_login, name="url_login"),
    path('logout/', views.fnct_logout, name="url_logout"),
    path('resetar/', views.fnct_resetar, name="url_resetar"),
    path('redefinindo/<str:token>', views.fnct_rdfnndo, name="url_rdfnndo"),
    path('enviar_email_restar_senha/', views.fnct_enviar_email_restar_senha,
         name="url_enviar_email_restar_senha"),
    path('upgrade_senha/<str:token>', views.fnct_upgrde_snha,
         name="url_fnct_upgrde_snha"),
    path('rcprr_usrnme/', views.fnct_rcprrusrnme, name="URL_rcprrusrnme"),
    path('agenda/', views.fnct_agenda, name="url_agenda"),
]
