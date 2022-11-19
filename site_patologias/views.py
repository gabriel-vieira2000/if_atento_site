from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd
import plotly.express as px
import requests
from dotenv import load_dotenv
import os 
import math
from hashlib import sha256

from .models import Admin
from .forms import CadastraAdminForm

load_dotenv()

lista_nomes_patologias = ["Infiltração", "Carbonatação ou Corrosão do Aço", "Deslocamento no revestimento", "Fissura ou Trincas", "Bolhas", "Vidro Quebrado", "Falta de iluminação", "Lixo ou sujeira acumulada"]
lista_cores_tipos_patologias = ["#003f5c","#2f4b7c", "#665191", "#a05195", "#d45087","#f95d6a", "#ff7c43","#ffa600"]

setores = ['Alojamento Masculino Bloco B', 'Hospital Veterinário', 'Prefeitura e Estacionamento', 'Canil', 'Granja de Frango de Corte']

# Views
def viewLogin(request):
    return render(request, 'login.html')

def validaLogin(request):
    if not request.POST:
        return viewLogin(request)

    email = request.POST["email"]
    senha = sha256(request.POST["senha"].encode('ascii')).hexdigest()
    admins = Admin.objects.all()
    for admin in admins:
        if admin.email == email and admin.senha == senha:
            request.session["usuario-autenticado"] = True
            print(request.session["usuario-autenticado"])
            return viewHome(request)
    return viewLogin(request)

def logout(request):
    if request.session.get("usuario-autenticado", None) == True:
        del request.session["usuario-autenticado"]
    return viewLogin(request)


def viewTabelaAdministradores(request, erro=None):
    #if request.session.get("usuario-autenticado", None) != True:
        #return viewLogin(request)

    mensagemErro = None
    if erro == 'erroCadastro':
        mensagemErro = "Houve um erro ao cadastrar o novo administrador! Por favor, atente às informações no formulário de cadastro e tente novamente."
    elif erro == 'erroExclusão':
        mensagemErro = "Erro ao excluir o usuário! Por favor, tente novamente!" 
    admins = Admin.objects.all()
    form = CadastraAdminForm()
    contexto = {
        'admins':admins,
        'form':form,
        'mensagemErro':mensagemErro
    }
    return render(request, 'administrador.html', context=contexto)

def cadastraAdmin(request):
    if not request.POST:
        return viewTabelaAdministradores(request)
    nomeAdmin = request.POST["nome"]
    emailAdmin = request.POST["email"]
    senhaAdmin = sha256(request.POST["senha"].encode('ascii')).hexdigest()
    novoAdmin = Admin(nome=nomeAdmin, email=emailAdmin, senha=senhaAdmin)
    admins = Admin.objects.all()
    for admin in admins:
        if admin.nome == novoAdmin.nome or admin.email == novoAdmin.email:
            return viewTabelaAdministradores(request, 'erroCadastro')
    novoAdmin.save()
    return viewTabelaAdministradores(request)

def deletaAdmin(request):
    if not request.POST or request.POST["id"] == "#":
        return viewTabelaAdministradores(request, 'erroExclusao')
    admin = Admin.objects.get(id=int(request.POST["id"]))
    admin.delete()
    return viewTabelaAdministradores(request)

def viewHome(request):
    if request.session.get("usuario-autenticado", None) != True:
        return viewLogin(request)

    caminho_pasta = os.path.dirname(__file__)
    dados_csv = os.path.join(caminho_pasta, 'dados_ocorrencias.csv')
    df = pd.read_csv(dados_csv)

    n_total_ocorrencias = df.shape[0]

    setor_mais_ocorrencias = df.groupby(["Nome do Setor"])["Nome do Setor"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    nome_setor_mais_ocorrencias = setor_mais_ocorrencias.iloc[0]["Nome do Setor"]
    n_ocorr_setor_mais_ocorrencias = setor_mais_ocorrencias.iloc[0]["Quantidade de Registros"]
    outros_setores_mais_ocorrencias = []
    for i in range (1,len(setor_mais_ocorrencias)):
        if i > 5:
            break
        outros_setores_mais_ocorrencias.append([setor_mais_ocorrencias.iloc[i]["Nome do Setor"], setor_mais_ocorrencias.iloc[i]["Quantidade de Registros"]])

    global lista_nomes_patologias
    ocorrencias_patologias = df.groupby(["Patologia"])["Patologia"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    tipo_patologia_maior_ocorrencia = lista_nomes_patologias[int(ocorrencias_patologias.iloc[0]["Patologia"])]
    n_ocorr_patologia_maior_ocorrencia = ocorrencias_patologias.iloc[0]["Quantidade de Registros"]

    ocorrencias_patologias = df.groupby(["Patologia"])["Patologia"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    tipo_patologia_maior_ocorrencia = lista_nomes_patologias[int(ocorrencias_patologias.iloc[0]["Patologia"])]
    n_ocorr_patologia_maior_ocorrencia = ocorrencias_patologias.iloc[0]["Quantidade de Registros"]

    ocorrencias_patologias = ocorrencias_patologias.values.tolist()
    for patologia in ocorrencias_patologias:
        patologia.append(lista_cores_tipos_patologias[int(patologia[0])])
        patologia[0] =  lista_nomes_patologias[int(patologia[0])]
    
    ocorrencias_por_dia = df.groupby("Data do Registro")["Data do Registro"].count().reset_index(name="Quantidade de Registros")
    ocorrencias_por_dia["Data do Registro Formatada"] = pd.to_datetime(ocorrencias_por_dia["Data do Registro"], format="%d/%m/%Y")
    ocorrencias_por_dia.sort_values(by="Data do Registro Formatada", inplace = True)
    dias = ocorrencias_por_dia["Data do Registro"].tolist()
    quantidade_ocorrencias = ocorrencias_por_dia["Quantidade de Registros"].tolist()

    dadosGrafico1_x = dias
    dadosGrafico1_y = quantidade_ocorrencias
    dadosGrafico2 = ocorrencias_patologias

    desvio_padrao_ocorrencias_por_dia = ocorrencias_por_dia["Quantidade de Registros"].std().round(2)
    media_ocorrencias_por_dia = float(ocorrencias_por_dia["Quantidade de Registros"].mean().round(1))
    mediana_ocorrencias_por_dia = float(ocorrencias_por_dia["Quantidade de Registros"].median().round(1))
    moda_ocorrencias_por_dia = float(ocorrencias_por_dia["Quantidade de Registros"].mode().round(1))

    contexto = {
        'n_total_ocorrencias':n_total_ocorrencias,
        'setor_mais_ocorrencias':nome_setor_mais_ocorrencias,
        'n_ocorr_setor_mais_ocorrencias':n_ocorr_setor_mais_ocorrencias,
        'outros_setores_mais_ocorrencias':outros_setores_mais_ocorrencias,
        'tipo_patologia_maior_ocorrencia':tipo_patologia_maior_ocorrencia,
        'n_ocorr_patologia_maior_ocorrencia':n_ocorr_patologia_maior_ocorrencia,
        'dadosGrafico1_x':dadosGrafico1_x,
        'dadosGrafico1_y':dadosGrafico1_y,
        'dadosGrafico2':dadosGrafico2,
        'desvio_padrao_ocorrencias_por_dia': desvio_padrao_ocorrencias_por_dia,
        'media_ocorrencias_por_dia':media_ocorrencias_por_dia,
        'mediana_ocorrencias_por_dia':mediana_ocorrencias_por_dia,
        'moda_ocorrencias_por_dia':moda_ocorrencias_por_dia
    }

    return render(request, 'home.html', context=contexto)

def viewTabelaOcorrencias(request):
    if request.session.get("usuario-autenticado", None) != True:
        return viewLogin(request)

    if request.session.get("usuario-autenticado", None) != True:
        return viewLogin(request)
    caminho_pasta = os.path.dirname(__file__)
    dados_csv = os.path.join(caminho_pasta, 'dados_ocorrencias.csv')
    df = pd.read_csv(dados_csv)
    df.drop("Unnamed: 0", axis=1, inplace=True)
    df["Patologia"].replace([0,1,2,3,4,5,6,7], lista_nomes_patologias, inplace=True)
    df["Tempo que vê a patologia"].replace([0,1,2], ["Primeira Vez que Vi", "Comecei a ver recentemente (< 1 ano)", "Já vejo a muito tempo? ( > 1 ano)"], inplace=True)
    df["É urgente?"].replace([0,1],['Sim', 'Não'],inplace=True)
    contexto = {'tabela_ocorrencias':df}
    print(df.info())

    return render(request, 'tabela_ocorrencias.html', context=contexto)

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

def viewSetores(request, idSetor):
    if request.session.get("usuario-autenticado", None) != True:
        return viewLogin(request)

    print(idSetor)
    print(setores[idSetor-1])

    caminho_pasta = os.path.dirname(__file__)
    dados_csv = os.path.join(caminho_pasta, 'dados_ocorrencias.csv')
    df = pd.read_csv(dados_csv)

    df.rename(columns={'Nome do Setor': 'NomeDoSetor', "É urgente?":"Urgente", "Tempo que vê a patologia":"TempoQueVe"}, inplace=True)
    condicao = "NomeDoSetor == '"+setores[idSetor-1]+"'"
    df = df.query(condicao)
    print(df["Urgente"])

    nomeSetor = setores[idSetor-1]

    setoresComID = []
    id = 1
    for setor in setores:
        setoresComID.append([id, setor])
        id += 1
    
    n_total_ocorrencias = df.shape[0]

    quantidadeUrgentes = int(df.query("Urgente == 1").shape[0])
    porcentagemUrgencia = math.floor((quantidadeUrgentes/int(n_total_ocorrencias)) * 100)

    global lista_nomes_patologias
    ocorrencias_patologias = df.groupby(["Patologia"])["Patologia"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    tipo_patologia_maior_ocorrencia = lista_nomes_patologias[int(ocorrencias_patologias.iloc[0]["Patologia"])]
    n_ocorr_patologia_maior_ocorrencia = ocorrencias_patologias.iloc[0]["Quantidade de Registros"]

    ocorrencias_patologias = df.groupby(["Patologia"])["Patologia"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    tipo_patologia_maior_ocorrencia = lista_nomes_patologias[int(ocorrencias_patologias.iloc[0]["Patologia"])]
    n_ocorr_patologia_maior_ocorrencia = ocorrencias_patologias.iloc[0]["Quantidade de Registros"]

    ocorrencias_patologias = ocorrencias_patologias.values.tolist()
    for patologia in ocorrencias_patologias:
        patologia.append(lista_cores_tipos_patologias[int(patologia[0])])
        patologia[0] =  lista_nomes_patologias[int(patologia[0])]
    
    ocorrencias_por_dia = df.groupby("Data do Registro")["Data do Registro"].count().reset_index(name="Quantidade de Registros")
    ocorrencias_por_dia["Data do Registro Formatada"] = pd.to_datetime(ocorrencias_por_dia["Data do Registro"], format="%d/%m/%Y")
    ocorrencias_por_dia.sort_values(by="Data do Registro Formatada", inplace = True)
    dias = ocorrencias_por_dia["Data do Registro"].tolist()
    quantidade_ocorrencias = ocorrencias_por_dia["Quantidade de Registros"].tolist()

    dias_ocorrencias_setor = df.groupby("Data do Registro")["Data do Registro"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    dia_mais_ocorrencias_setor = dias_ocorrencias_setor.iloc[0]["Data do Registro"]
    qtd_registros_dia_mais_ocorrencias_setor = dias_ocorrencias_setor.iloc[0]["Quantidade de Registros"]

    porcentagemPrimeiraVezViu = int(df.query("TempoQueVe == 0").shape[0])
    porcentagemPrimeiraVezViu = math.floor((porcentagemPrimeiraVezViu/int(n_total_ocorrencias)) * 100)
    quantidadePrimeiraVezViu = int(df.query("TempoQueVe == 0").shape[0])
    
    porcentagemComecouRecentemente = int(df.query("TempoQueVe == 1").shape[0])
    porcentagemComecouRecentemente = math.floor((porcentagemComecouRecentemente/int(n_total_ocorrencias)) * 100)
    quantidadeComecouRecentemente = int(df.query("TempoQueVe == 1").shape[0])

    porcentagemVeFazTempo = int(df.query("TempoQueVe == 2").shape[0])
    porcentagemVeFazTempo = math.floor((porcentagemVeFazTempo/int(n_total_ocorrencias)) * 100)
    quantidadeVeFazTempo = int(df.query("TempoQueVe == 2").shape[0])
    
    print(porcentagemPrimeiraVezViu)
    print(quantidadePrimeiraVezViu)
    print(porcentagemComecouRecentemente)
    print(quantidadeComecouRecentemente)
    print(porcentagemVeFazTempo)
    print(quantidadeVeFazTempo)

    dadosGrafico1_x = dias
    dadosGrafico1_y = quantidade_ocorrencias
    dadosGrafico2 = ocorrencias_patologias

    contexto = {
        'nomeSetor': nomeSetor,
        'setores': setoresComID,
        'n_total_ocorrencias':n_total_ocorrencias,
        'porcentagemUrgencia': porcentagemUrgencia,
        'dia_mais_ocorrencias_setor':dia_mais_ocorrencias_setor,
        'qtd_registros_dia_mais_ocorrencias_setor':qtd_registros_dia_mais_ocorrencias_setor,
        'tipo_patologia_maior_ocorrencia': tipo_patologia_maior_ocorrencia,
        'n_ocorr_patologia_maior_ocorrencia': n_ocorr_patologia_maior_ocorrencia,
        'porcentagemPrimeiraVezViu':porcentagemPrimeiraVezViu,
        'quantidadePrimeiraVezViu':quantidadePrimeiraVezViu,
        'porcentagemComecouRecentemente':porcentagemComecouRecentemente,
        'quantidadeComecouRecentemente':quantidadeComecouRecentemente,
        'porcentagemVeFazTempo':porcentagemVeFazTempo,
        'quantidadeVeFazTempo':quantidadeVeFazTempo,
        'dadosGrafico1_x': dadosGrafico1_x,
        'dadosGrafico1_y': dadosGrafico1_y,
        'dadosGrafico2': dadosGrafico2
    }

    return render(request, 'setor.html', context=contexto)


def viewPatologias(request, idPatologia):
    if request.session.get("usuario-autenticado", None) != True:
        return viewLogin(request)
    
    global lista_nomes_patologias
    nomePatologia = lista_nomes_patologias[idPatologia]

    nomesPatologiasComID = []
    for i in range(0, len(lista_nomes_patologias)):
        nomesPatologiasComID.append([i, lista_nomes_patologias[i]])

    caminho_pasta = os.path.dirname(__file__)
    dados_csv = os.path.join(caminho_pasta, 'dados_ocorrencias.csv')
    df = pd.read_csv(dados_csv)

    df.rename(columns={'Nome do Setor': 'NomeDoSetor', "É urgente?":"Urgente", "Tempo que vê a patologia":"TempoQueVe"}, inplace=True)
    condicao = "Patologia == "+str(idPatologia)
    df = df.query(condicao)

    n_total_ocorrencias = df.shape[0]
    print(n_total_ocorrencias)

    setor_mais_ocorrencias = df.groupby(["NomeDoSetor"])["NomeDoSetor"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    nome_setor_mais_ocorrencias = setor_mais_ocorrencias.iloc[0]["NomeDoSetor"]
    n_ocorr_setor_mais_ocorrencias = setor_mais_ocorrencias.iloc[0]["Quantidade de Registros"]
    
    quantidadeUrgentes = int(df.query("Urgente == 1").shape[0])
    porcentagemUrgencia = math.floor((quantidadeUrgentes/int(n_total_ocorrencias)) * 100)

    dias_ocorrencias_patologia = df.groupby("Data do Registro")["Data do Registro"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    dia_mais_ocorrencias_patologia = dias_ocorrencias_patologia.iloc[0]["Data do Registro"]
    qtd_registros_dia_mais_ocorrencias_patologia = dias_ocorrencias_patologia.iloc[0]["Quantidade de Registros"]

    porcentagemPrimeiraVezViu = int(df.query("TempoQueVe == 0").shape[0])
    porcentagemPrimeiraVezViu = math.floor((porcentagemPrimeiraVezViu/int(n_total_ocorrencias)) * 100)
    quantidadePrimeiraVezViu = int(df.query("TempoQueVe == 0").shape[0])
    
    porcentagemComecouRecentemente = int(df.query("TempoQueVe == 1").shape[0])
    porcentagemComecouRecentemente = math.floor((porcentagemComecouRecentemente/int(n_total_ocorrencias)) * 100)
    quantidadeComecouRecentemente = int(df.query("TempoQueVe == 1").shape[0])

    porcentagemVeFazTempo = int(df.query("TempoQueVe == 2").shape[0])
    porcentagemVeFazTempo = math.floor((porcentagemVeFazTempo/int(n_total_ocorrencias)) * 100)
    quantidadeVeFazTempo = int(df.query("TempoQueVe == 2").shape[0])

    global lista_cores_tipos_patologias
    setores_ocorrencia = df.groupby(["NomeDoSetor"])["NomeDoSetor"].count().reset_index(name="Quantidade de Registros")
    dadosGrafico2 = []
    for i in range(0,len(setores_ocorrencia)):
        dadosGrafico2.append([setor_mais_ocorrencias.iloc[i]["NomeDoSetor"], setor_mais_ocorrencias.iloc[i]["Quantidade de Registros"], lista_cores_tipos_patologias[i%8]])

    ocorrencias_patologias = df.groupby(["Patologia"])["Patologia"].count().reset_index(name="Quantidade de Registros").sort_values(by="Quantidade de Registros", ascending=False)
    tipo_patologia_maior_ocorrencia = lista_nomes_patologias[int(ocorrencias_patologias.iloc[0]["Patologia"])]
    n_ocorr_patologia_maior_ocorrencia = ocorrencias_patologias.iloc[0]["Quantidade de Registros"]

    ocorrencias_patologias = ocorrencias_patologias.values.tolist()
    for patologia in ocorrencias_patologias:
        patologia.append(lista_cores_tipos_patologias[int(patologia[0])])
        patologia[0] =  lista_nomes_patologias[int(patologia[0])]

    ocorrencias_por_dia = df.groupby("Data do Registro")["Data do Registro"].count().reset_index(name="Quantidade de Registros")
    ocorrencias_por_dia["Data do Registro Formatada"] = pd.to_datetime(ocorrencias_por_dia["Data do Registro"], format="%d/%m/%Y")
    ocorrencias_por_dia.sort_values(by="Data do Registro Formatada", inplace = True)
    dias = ocorrencias_por_dia["Data do Registro"].tolist()
    quantidade_ocorrencias = ocorrencias_por_dia["Quantidade de Registros"].tolist()    
 
    dadosGrafico1_x = dias
    dadosGrafico1_y = quantidade_ocorrencias

    contexto = {
        'nomePatologia': nomePatologia,
        'patologias': nomesPatologiasComID,
        'n_total_ocorrencias':n_total_ocorrencias,
        'porcentagemUrgencia': porcentagemUrgencia,
        'dia_mais_ocorrencias_patologia': dia_mais_ocorrencias_patologia,
        'qtd_registros_dia_mais_ocorrencias_patologia': qtd_registros_dia_mais_ocorrencias_patologia,
        'setor_mais_ocorrencias':nome_setor_mais_ocorrencias,
        'n_ocorr_setor_mais_ocorrencias':n_ocorr_setor_mais_ocorrencias,
        'porcentagemPrimeiraVezViu':porcentagemPrimeiraVezViu,
        'quantidadePrimeiraVezViu':quantidadePrimeiraVezViu,
        'porcentagemComecouRecentemente':porcentagemComecouRecentemente,
        'quantidadeComecouRecentemente':quantidadeComecouRecentemente,
        'porcentagemVeFazTempo':porcentagemVeFazTempo,
        'quantidadeVeFazTempo':quantidadeVeFazTempo,
        'dadosGrafico1_x':dias,
        'dadosGrafico1_y':quantidade_ocorrencias,
        'dadosGrafico2': dadosGrafico2
    }
    return render(request, 'patologia.html', context=contexto)

    
