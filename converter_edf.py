    # VERSAO COM 16 CANAIS NORMAL
    # traz a ferramenta que sabe ler arquivos .edf
    # import pyedflib
    # # traz o numpy, usado internamente para organizar os números
    # import numpy as np
    # # traz a ferramenta de tempo, pra gerar o timestamp
    # import time

    # # abre o arquivo .edf baixado do PhysioNet
    # arquivo = pyedflib.EdfReader("S001R01.edf")  # S001R03.edf(imaginação)  S001R02.edf(olhos fechados)

    # # define quantos canais vamos usar (16, para bater com o nosso projeto)
    # num_canais = 16
    # # lê o sinal de cada um dos 16 primeiros canais, guardando numa lista
    # sinais = [arquivo.readSignal(i) for i in range(num_canais)]
    # # fecha o arquivo, já que terminamos de ler
    # arquivo.close()

    # # descobre quantas amostras (pontos no tempo) existem, olhando o primeiro canal
    # num_amostras = len(sinais[0])

    # # abre (cria) o arquivo de saída, no formato que nosso código já sabe usar
    # with open("gravacao_olhos_abertos.csv", "w") as f: # gravacao_ruido.csv gravacao_olhos_fechados.csv
    #     # repete uma vez para cada amostra
    #     for i in range(num_amostras):
    #         # índice da amostra, reiniciando em ciclos de 0 a 255
    #         sample_index = i % 256
    #         # pega o valor de cada um dos 16 canais, nessa amostra específica
    #         exg = [sinais[canal][i] for canal in range(num_canais)]
    #         # preenche o resto das colunas com zero (não temos esses dados extras)
    #         resto_zeros = [0.0] * 13
    #         # pega o horário atual
    #         timestamp = time.time()
    #         # marcador zerado (nenhum evento marcado)
    #         marker = 0.0

    #         # junta tudo numa linha só
    #         linha = [sample_index] + exg + resto_zeros + [timestamp, marker]
    #         # escreve a linha no arquivo, separada por tab
    #         f.write("\t".join(map(str, linha)) + "\n")

    # print(f"Convertido! {num_amostras} amostras salvas em gravacao_ruido.csv")

    # VERSAO COM A LEITURA DOS 64 CANAIS DO ARQUIVO
# traz a ferramenta que sabe ler arquivos .edf
import pyedflib
# traz o numpy, usado internamente para organizar os números
import numpy as np
# traz a ferramenta de tempo, pra gerar o timestamp
import time

# abre o arquivo .edf baixado do PhysioNet
arquivo = pyedflib.EdfReader("S001R03.edf")  # S001R03.edf(imaginação)  S001R02.edf(olhos fechados) S001R01.edf(olhos abertos)

# pega os NOMES reais de todos os 64 canais do arquivo
nomes_canais = arquivo.getSignalLabels()

# lista dos eletrodos que realmente nos interessam
eletrodos_desejados = ["C3..", "C4..", "O1..", "O2.."]

# procura o índice certo de cada eletrodo, pelo NOME (não mais um número fixo)
indices_corretos = [nomes_canais.index(nome) for nome in eletrodos_desejados]

# mostra na tela os índices encontrados, pra confirmar que bateu com o esperado
print("Índices encontrados:", indices_corretos)

# lê o sinal de cada eletrodo desejado, usando os índices certos
sinais_reais = [arquivo.readSignal(i) for i in indices_corretos]

# pega a taxa de amostragem REAL do arquivo (antes usávamos 125 fixo, errado)
fs_real = arquivo.getSampleFrequency(0)

# fecha o arquivo, já que terminamos de ler
arquivo.close()

# descobre quantas amostras existem, olhando o primeiro canal lido
num_amostras = len(sinais_reais[0])

# abre (cria) o arquivo de saída, no formato que nosso código já sabe usar
with open("gravacao_ruido.csv", "w") as f: # gravacao_ruido.csv gravacao_olhos_fechados.csv gravacao_olhos_abertos.csv
    # repete uma vez para cada amostra
    for i in range(num_amostras):
        # índice da amostra, reiniciando em ciclos de 0 a 255
        sample_index = i % 256

        # monta os 16 "slots" de canal, preenchendo só os 4 que temos de verdade
        # nas mesmas posições que o resto do projeto já espera (Cyton+Daisy)
        exg = [0.0] * 16
        exg[2] = sinais_reais[0][i]  # C3
        exg[3] = sinais_reais[1][i]  # C4
        exg[6] = sinais_reais[2][i]  # O1
        exg[7] = sinais_reais[3][i]  # O2

        # preenche o resto das colunas com zero
        resto_zeros = [0.0] * 13
        # pega o horário atual
        timestamp = time.time()
        # marcador zerado
        marker = 0.0

        # junta tudo numa linha só
        linha = [sample_index] + exg + resto_zeros + [timestamp, marker]
        # escreve a linha no arquivo, separada por tab
        f.write("\t".join(map(str, linha)) + "\n")

# avisa na tela, já mostrando a taxa real confirmada
print(f"Convertido! {num_amostras} amostras (taxa real: {fs_real}Hz) salvas em gravacao_olhos_abertos.csv")