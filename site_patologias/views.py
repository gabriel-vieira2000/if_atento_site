from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd
import plotly.express as px
import requests
from dotenv import load_dotenv
import os 
load_dotenv()

lista_nomes_patologias = ["Infiltração", "Carbonatação ou Corrosão do Aço", "Deslocamento no revestimento", "Fissura ou Trincas", "Bolhas", "Vidro Quebrado", "Falta de iluminação", "Lixo ou sujeira acumulada"]

# Create your views here.
def viewHome(request):

    caminho_pasta = os.path.dirname(__file__)
    dados_csv = os.path.join(caminho_pasta, 'dados_ocorrencias.csv')
    df = pd.read_csv(dados_csv)

    n_total_ocorrencias = df.shape[0]

    setor_mais_ocorrencias = df.groupby(["Nome do Setor"])["Nome do Setor"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros")
    nome_setor_mais_ocorrencias = setor_mais_ocorrencias.loc[0]["Nome do Setor"]
    n_ocorr_setor_mais_ocorrencias = setor_mais_ocorrencias.loc[0]["Quantidade de Registros"]

    global lista_nomes_patologias
    patologia_mais_ocorrencias = df.groupby(["Patologia"])["Patologia"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros")
    tipo_patologia_maior_ocorrencia = lista_nomes_patologias[int(patologia_mais_ocorrencias.loc[0]["Patologia"])]
    n_ocorr_patologia_maior_ocorrencia = patologia_mais_ocorrencias.loc[0]["Quantidade de Registros"]
    
    contexto = {
        'n_total_ocorrencias':n_total_ocorrencias,
        'setor_mais_ocorrencias':nome_setor_mais_ocorrencias,
        'n_ocorr_setor_mais_ocorrencias':n_ocorr_setor_mais_ocorrencias,
        'tipo_patologia_maior_ocorrencia':tipo_patologia_maior_ocorrencia,
        'n_ocorr_patologia_maior_ocorrencia':n_ocorr_patologia_maior_ocorrencia
    }

    return render(request, 'home.html', context=contexto)

def viewTabelaOcorrencias(request):
    caminho_pasta = os.path.dirname(__file__)
    dados_csv = os.path.join(caminho_pasta, 'dados_ocorrencias.csv')
    df = pd.read_csv(dados_csv)
    df.drop("Unnamed: 0", axis=1)
    contexto = {'tabela_ocorrencias':df}

    return render(request, 'tabela_ocorrencias.html', context=contexto)

def testeGrafico(request):
    df = pd.DataFrame(dict(
        x = [1, 3, 2, 4],
        y = [1, 2, 3, 4]
    ))
    
    fig = px.line(df, x="x", y="y", title="Teste de Gráfico")
    grafico = fig.to_html()
    return render(request, 'home.html', context=contexto)

def atualiza_dados(request):
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
    df.to_csv('dados_ocorrencias.csv')
    contexto = {'tabela_ocorrencias':df}

    return render(request, 'tabela_ocorrencias.html', context=contexto)

    
