"""if_atento_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from site_patologias.views import viewLogin, viewHome, viewTabelaOcorrencias, atualizaDadosCSV, viewSetores, viewPatologias, viewTabelaAdministradores, cadastraAdmin, deletaAdmin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',viewLogin),
    path('login/', viewLogin),
    path('administradores/', viewTabelaAdministradores),
    path('administradores/<str:erro>', viewTabelaAdministradores),
    path('cadastro/admin', cadastraAdmin),
    path('exclusao/admin', deletaAdmin),
    path('home/', viewHome),
    path('ocorrencias/', viewTabelaOcorrencias),
    path('atualizaDados/', atualizaDadosCSV),
    path('setores/<int:idSetor>', viewSetores),
    path('patologias/<int:idPatologia>', viewPatologias), 
]
