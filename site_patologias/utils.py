import matplotlib.pyplot as plt
import matplotlib
import base64
from io import BytesIO

def geraImagemGrafico():
    buffer = BytesIO
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    imagem_grafico = buffer.getvalue()
    grafico = base64.b64enconde(imagem_grafico)
    grafico = grafico.decode('utf-8')
    buffer.close()
    return grafico

def geraGrafico(x, y, x_nome, y_nome, titulo):
    plt.switch_backend('AGG')
    font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
    matplotlib.rc('font', **font)
    plt.figure(figsize=(20,15))
    plt.title(titulo)
    plt.xlabel(x_nome)
    plt.ylabel(y_nome)
    plt.plot(x,y)

    plt.xticks(rotation=45)
    plt.tight_layout()
    grafico = geraImagemGrafico()
    return grafico

