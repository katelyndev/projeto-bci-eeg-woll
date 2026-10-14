# traz o numpy, usado pra fazer contas com os números do sinal
import numpy as np

# traz a função welch, que calcula a força de cada frequência no sinal
from scipy.signal import welch

# traz o DataFilter, usado pra ler o arquivo CSV com o sinal gravado
from brainflow.data_filter import DataFilter

# define uma função que calcula a potência da Alfa num arquivo específico
def calcular_potencia_alfa(nome_arquivo, indice_canal, fs=160):

    # lê o arquivo CSV inteiro
    dados = DataFilter.read_file(nome_arquivo)

    # pega só a linha do canal que queremos (O1, na posição 7)
    canal = dados[indice_canal]

    # calcula a força de cada frequência presente nesse canal
    freqs, psd = welch(canal, fs=fs)

    # acha as posições onde a frequência está entre 8 e 13Hz (faixa da Alfa)
    indices_alfa = np.where((freqs >= 8) & (freqs <= 13))[0]

    # calcula a média de potência só nessa faixa
    potencia_alfa = np.mean(psd[indices_alfa])

    # mostra na tela o nome do arquivo JUNTO do resultado, pra não ter dúvida
    print(f"Arquivo: {nome_arquivo} | Potência Alfa: {potencia_alfa:.2f}")

    # devolve o valor calculado
    return potencia_alfa

# # roda a função pro arquivo de olhos FECHADOS
# calcular_potencia_alfa('gravacao_olhos_fechados.csv', 7)

# # roda a função pro arquivo de olhos ABERTOS
# calcular_potencia_alfa('gravacao_olhos_abertos.csv', 7)

# também testa os arquivos JÁ FILTRADOS pelo seu código (8-13Hz), 
# pra confirmar se o filtro realmente concentrou a energia em Alfa
calcular_potencia_alfa('gravacao_olhos_fechados_filtrada.csv', 7)
calcular_potencia_alfa('gravacao_olhos_abertos_filtrada.csv', 7)