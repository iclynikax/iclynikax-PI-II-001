from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.fnct_cdstro, name="url_cadastro"),
    path('login/', views.fnct_login , name="url_login"),
    path('logout/', views.fnct_logout, name="url_logout"),
    path('resetar/', views.fnct_resetar , name="url_resetar"),
    path('rcprr_usrnme/', views.fnct_rcprrusrnme, name="URL_rcprrusrnme"), 
]