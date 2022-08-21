from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd
import plotly.express as px

# Create your views here.
def viewHome(request):
    return HttpResponse("Olá Mundão!")

def testeGrafico(request):
    df = pd.DataFrame(dict(
        x = [1, 3, 2, 4],
        y = [1, 2, 3, 4]
    ))
    
    fig = px.line(df, x="x", y="y", title="Teste de Gráfico")
    grafico = fig.to_html()
    contexto = {'grafico':grafico}

    print(df.head())
    return render(request, 'home.html', context=contexto)