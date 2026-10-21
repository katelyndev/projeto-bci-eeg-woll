# traz o numpy, ferramenta pra trabalhar com números e listas de forma eficiente
import numpy as np

# traz a função welch, que calcula a força de cada frequência dentro de um sinal
from scipy.signal import welch

# traz o DataFilter, ferramenta do BrainFlow pra ler os arquivos CSV
# from brainflow.data_filter import DataFilter

import pyedflib

# define a função que calcula a potência de UMA faixa de frequência específica
# ela recebe: o nome do arquivo, qual canal usar, o início e fim da faixa, 
# um nome pra identificar a faixa no print, e a taxa de amostragem (fixa em 160)
def calcular_potencia_banda(nome_arquivo, indice_canal, freq_min, freq_max, nome_banda, fs=160):

    # # lê o arquivo CSV inteiro e guarda o conteúdo numa variável
    # dados = DataFilter.read_file(nome_arquivo)

    # # pega só a linha do canal que escolhemos (ex: canal O1)
    # canal = dados[indice_canal]

    #  abre o arquivo .edf, preparando para ser lido
    arquivo = pyedflib.EdfReader(nome_arquivo)

    # pega do arquivo o sinal do canal excolhido
    canal = arquivo.readSignal(indice_canal)
    # pergunta para o arquivo qual a taxa de amostragem real do canal 
    fs = arquivo.getSampleFrequency(indice_canal)
    # fecha o arquivo avisando que j erminamos de usar ele 
    arquivo.close()


    # calcula a força de cada frequência presente nesse canal
    freqs, psd = welch(canal, fs=fs)

    # descobre quais posições da lista de frequências estão DENTRO da faixa pedida
    indices_banda = np.where((freqs >= freq_min) & (freqs <= freq_max))[0]

    # calcula a média da força, só das posições que estão dentro da faixa
    potencia_banda = np.mean(psd[indices_banda])

    # mostra na tela o resultado, já identificando arquivo, faixa e banda
    print(f"Arquivo: {nome_arquivo} | Banda {nome_banda} ({freq_min}-{freq_max}Hz) | Potência: {potencia_banda:.2f}")

    # devolve o valor calculado, caso alguém queira usar depois
    return potencia_banda

calcular_potencia_banda('Subject00_1.edf', 0, 13, 30, "Beta")

# # imprime um título, só pra organizar visualmente o que vai aparecer no terminal
# print("--- Arquivo ORIGINAL (sem filtro) ---")

# # calcula a potência da Alfa (8-13Hz) no arquivo SEM filtro
# # calcular_potencia_banda('gravacao_olhos_fechados.csv', 7, 8, 13, "Alfa")

# # calcula a potência da Beta (13-30Hz) no mesmo arquivo SEM filtro
# calcular_potencia_banda('gravacao_olhos_fechados.csv', 7, 13, 30, "Beta")

# # imprime outro título, pra separar visualmente a próxima parte
# print("--- Arquivo FILTRADO (8-13Hz) ---")

# # calcula a potência da Alfa (8-13Hz) no arquivo JÁ FILTRADO
# # calcular_potencia_banda('gravacao_olhos_fechados_filtrada.csv', 7, 8, 13, "Alfa")

# # calcula a potência da Beta (13-30Hz) no arquivo JÁ FILTRADO
# # calcular_potencia_banda('gravacao_olhos_fechados_filtrada.csv', 7, 13, 30, "Beta")

# print("--- Canal 8 (O2) - ORIGINAL (sem filtro) ---")
# # calcular_potencia_banda('gravacao_olhos_fechados.csv', 8, 8, 13, "Alfa")
# calcular_potencia_banda('gravacao_olhos_fechados.csv', 8, 13, 30, "Beta")

# print("--- Canal 8 (O2) - FILTRADO (8-13Hz) ---")
# # calcular_potencia_banda('gravacao_olhos_fechados_corrigida.csv', 8, 8, 13, "Alfa")
# calcular_potencia_banda('gravacao_olhos_fechados_corrigida.csv', 8, 13, 30, "Beta")