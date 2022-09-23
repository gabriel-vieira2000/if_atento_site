from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd
import plotly.express as px
import requests
from dotenv import load_dotenv
import os 

from .utils import geraGrafico

load_dotenv()

lista_nomes_patologias = ["Infiltração", "Carbonatação ou Corrosão do Aço", "Deslocamento no revestimento", "Fissura ou Trincas", "Bolhas", "Vidro Quebrado", "Falta de iluminação", "Lixo ou sujeira acumulada"]
lista_cores_tipos_patologias = ["#003f5c","#2f4b7c", "#665191", "#a05195", "#d45087","#f95d6a", "#ff7c43","#ffa600"]

# Views
def viewHome(request):
    caminho_pasta = os.path.dirname(__file__)
    dados_csv = os.path.join(caminho_pasta, 'dados_ocorrencias.csv')
    df = pd.read_csv(dados_csv)

    n_total_ocorrencias = df.shape[0]

    setor_mais_ocorrencias = df.groupby(["Nome do Setor"])["Nome do Setor"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros")
    nome_setor_mais_ocorrencias = setor_mais_ocorrencias.loc[0]["Nome do Setor"]
    n_ocorr_setor_mais_ocorrencias = setor_mais_ocorrencias.loc[0]["Quantidade de Registros"]

    global lista_nomes_patologias
    ocorrencias_patologias = df.groupby(["Patologia"])["Patologia"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros")

    tipo_patologia_maior_ocorrencia = lista_nomes_patologias[int(ocorrencias_patologias.loc[0]["Patologia"])]
    n_ocorr_patologia_maior_ocorrencia = ocorrencias_patologias.loc[0]["Quantidade de Registros"]

    cores_patologias = []
    tipos_patologias = ocorrencias_patologias["Patologia"].tolist()
    for i, tipo_patologia in enumerate(tipos_patologias):
        print(tipo_patologia)
        tipos_patologias[i] = lista_nomes_patologias[(int(tipo_patologia)-2)]
        cores_patologias.append(lista_cores_tipos_patologias[(int(tipo_patologia)-2)])
    print(tipos_patologias)
    qtd_ocorrencias_patologias = ocorrencias_patologias["Quantidade de Registros"].tolist()
    qtd_tipos_patologias = ocorrencias_patologias.shape[0]
    
    ocorrencias_por_dia = df.groupby("Data do Registro")["Data do Registro"].count().reset_index(name="Quantidade de Registros").sort_values(by="Data do Registro", ascending=True)
    dias = ocorrencias_por_dia["Data do Registro"].tolist()
    quantidade_ocorrencias = ocorrencias_por_dia["Quantidade de Registros"].tolist()

    print(dias)
    print(quantidade_ocorrencias)

    dadosGrafico1_x = dias
    dadosGrafico1_y = quantidade_ocorrencias
    dadosGrafico2_x = tipos_patologias
    dadosGrafico2_y = quantidade_ocorrencias

    contexto = {
        'n_total_ocorrencias':n_total_ocorrencias,
        'setor_mais_ocorrencias':nome_setor_mais_ocorrencias,
        'n_ocorr_setor_mais_ocorrencias':n_ocorr_setor_mais_ocorrencias,
        'tipo_patologia_maior_ocorrencia':tipo_patologia_maior_ocorrencia,
        'n_ocorr_patologia_maior_ocorrencia':n_ocorr_patologia_maior_ocorrencia,
        'qtd_tipos_patologias':qtd_tipos_patologias,
        'cores_patologias':cores_patologias,
        'dadosGrafico1_x':dadosGrafico1_x,
        'dadosGrafico1_y':dadosGrafico1_y,
        'dadosGrafico2_x':dadosGrafico2_x,
        'dadosGrafico2_y':dadosGrafico2_y
    }

    return render(request, 'home.html', context=contexto)

def viewTabelaOcorrencias(request):
    caminho_pasta = os.path.dirname(__file__)
    dados_csv = os.path.join(caminho_pasta, 'dados_ocorrencias.csv')
    df = pd.read_csv(dados_csv)
    df.drop("Unnamed: 0", axis=1, inplace=True)
    contexto = {'tabela_ocorrencias':df}
    print(df.info())

    return render(request, 'tabela_ocorrencias.html', context=contexto)

def testeGrafico(request):
    df = pd.DataFrame(dict(
        x = [1, 3, 2, 4],
        y = [1, 2, 3, 4]
    ))
    
    fig = px.line(df, x="x", y="y", title="Teste de Gráfico")
    grafico = fig.to_html()
    return render(request, 'home.html', context=contexto)

def atualizaDadosCSV(request):
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
    df.to_csv('./site_patologias/dados_ocorrencias.csv')
    contexto = {'tabela_ocorrencias':df}

    return viewTabelaOcorrencias(request)

    
