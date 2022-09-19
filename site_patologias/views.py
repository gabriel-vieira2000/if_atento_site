from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd
import plotly.express as px
import requests
from dotenv import load_dotenv
import os 
load_dotenv()

# Create your views here.
def viewHome(request):
    return HttpResponse()

def testeGrafico(request):
    df = pd.DataFrame(dict(
        x = [1, 3, 2, 4],
        y = [1, 2, 3, 4]
    ))
    
    fig = px.line(df, x="x", y="y", title="Teste de Gráfico")
    grafico = fig.to_html()

    setor_mais_ocorrencias = "Alojamento Masculino Bloco B"
    n_ocorr_setor_mais_ocorrencias = 12

    tipo_patologia_maior_ocorrencia = "Infiltração"

    contexto = {'grafico1':grafico,
                'setor_mais_ocorrencias':setor_mais_ocorrencias,
                'n_ocorr_setor_mais_ocorrencias':n_ocorr_setor_mais_ocorrencias,
                'tipo_patologia_maior_ocorrencia':tipo_patologia_maior_ocorrencia}

    print(df.head())
    return render(request, 'home.html', context=contexto)

def tabela_ocorrencias(request):
    api_url = str(os.getenv('API_BASE_URL'))+"/ocorrencias"
    req = requests.get(api_url)
    dados = dict(req.json())
    chaves = []

    for registro in dados["results"]:
        chaves.append(registro["key"])

    registros_ocorrencias = []
    for chave in chaves:
        url = api_url + "/" + chave
        req = requests.get(url)
        dados = dict(req.json())
        registros_ocorrencias.append([dados['props']['nomeSetor'],dados['props']['patologia'],dados['props']['tempoPatologia'],dados['props']['urgencia'],dados['props']['textoDetalhes'],dados['props']['dataRegistro'],dados['props']['foto']])
    print(registros_ocorrencias)

    df = pd.DataFrame(registros_ocorrencias, columns=['Nome do Setor', 'Patologia', 'Tempo que vê a patologia','É urgente?','Detalhes','Data do Registro','Foto'])
    contexto = {'tabela_ocorrencias':df}

    return render(request, 'tabela_ocorrencias.html', context=contexto)
