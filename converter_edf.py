# traz a ferramenta que sabe ler arquivos .edf
import pyedflib
# traz o numpy, usado internamente para organizar os números
import numpy as np
# traz a ferramenta de tempo, pra gerar o timestamp
import time

# abre o arquivo .edf baixado do PhysioNet
arquivo = pyedflib.EdfReader("S001R03.edf")

# define quantos canais vamos usar (16, para bater com o nosso projeto)
num_canais = 16
# lê o sinal de cada um dos 16 primeiros canais, guardando numa lista
sinais = [arquivo.readSignal(i) for i in range(num_canais)]
# fecha o arquivo, já que terminamos de ler
arquivo.close()

# descobre quantas amostras (pontos no tempo) existem, olhando o primeiro canal
num_amostras = len(sinais[0])

# abre (cria) o arquivo de saída, no formato que nosso código já sabe usar
with open("gravacao_ruido.csv", "w") as f:
    # repete uma vez para cada amostra
    for i in range(num_amostras):
        # índice da amostra, reiniciando em ciclos de 0 a 255
        sample_index = i % 256
        # pega o valor de cada um dos 16 canais, nessa amostra específica
        exg = [sinais[canal][i] for canal in range(num_canais)]
        # preenche o resto das colunas com zero (não temos esses dados extras)
        resto_zeros = [0.0] * 13
        # pega o horário atual
        timestamp = time.time()
        # marcador zerado (nenhum evento marcado)
        marker = 0.0

        # junta tudo numa linha só
        linha = [sample_index] + exg + resto_zeros + [timestamp, marker]
        # escreve a linha no arquivo, separada por tab
        f.write("\t".join(map(str, linha)) + "\n")

print(f"Convertido! {num_amostras} amostras salvas em gravacao_ruido.csv")