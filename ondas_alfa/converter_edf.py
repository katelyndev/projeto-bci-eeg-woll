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

# ====================================================================================
# Converte gravações .edf do PhysioNet para CSV no formato do BrainFlow.
# Escolhe os 16 canais pelo NOME e usa a taxa de amostragem real do arquivo.

# VERSAO COM A LEITURA DOS CANAIS DO ARQUIVO
# traz a ferramenta que sabe ler arquivos .edf
import pyedflib
# traz o numpy, usado internamente para organizar os números
import numpy as np
# traz a ferramenta de tempo, pra gerar o timestamp
import time

# abre o arquivo .edf baixado do PhysioNet
arquivo = pyedflib.EdfReader("S003R01.edf")  # S001R03.edf(imaginação)  S001R02.edf(olhos fechados) S001R01.edf(olhos abertos)

# pega os NOMES reais de todos os 64 canais do arquivo
nomes_canais = arquivo.getSignalLabels()

# lista dos 16 eletrodos padrão do Cyton+Daisy, NA MESMA ORDEM que o projeto já usa
eletrodos_desejados = [
    "Fp1.", "Fp2.", "C3..", "C4..", "P7..", "P8..", "O1..", "O2..",
    "F7..", "F8..", "F3..", "F4..", "T7..", "T8..", "P3..", "P4..",
]

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

# ponto de referência para calcular os demais timestamps
timestamp_inicial = time.time()

# abre (cria) o arquivo de saída, no formato que nosso código já sabe usar
with open("gravacao_olhos_abertos_teste3.csv", "w") as f: # gravacao_ruido.csv gravacao_olhos_fechados.csv gravacao_olhos_abertos.csv
    # repete uma vez para cada amostra
    for i in range(num_amostras):
        # índice da amostra, reiniciando em ciclos de 0 a 255
        sample_index = i % 256

        # monta os 16 dados de canal
        # nas mesmas posições que o resto do projeto já espera (Cyton+Daisy)
        exg = [sinais_reais[canal][i] for canal in range(16)]


        # preenche o resto das colunas com zero
        resto_zeros = [0.0] * 13
        # pega o horário atual
        timestamp = time.time()

        # gera o timestamp certo, respeitando a taxa real de 160Hz
        timestamp = i / fs_real

        timestamp = timestamp_inicial + (i / fs_real)
        # marcador zerado
        marker = 0.0

        # junta tudo numa linha só
        linha = [sample_index] + exg + resto_zeros + [timestamp, marker]
        # escreve a linha no arquivo, separada por tab
        f.write("\t".join(map(str, linha)) + "\n")

# avisa na tela, já mostrando a taxa real confirmada
print(f"Convertido! {num_amostras} amostras (taxa real: {fs_real}Hz) salvas")

#  ==================================================================================

# LE O ARQUIVO .EDF, PEGA OS 16 CANAIS E SALVA EM CSV COM ANOTACOES DO QUE É LADO DIRETIO E ESQUERDO  
# # traz a ferramenta de ler arquivos .edf
# import pyedflib

# # traz o numpy, pra trabalhar com os números
# import numpy as np

# # lista com os nomes reais dos 16 eletrodos que o Cyton+Daisy usa
# nomes_eletrodos = [
#     "Fp1", "Fp2", "C3", "C4", "P7", "P8", "O1", "O2",
#     "F7", "F8", "F3", "F4", "T7", "T8", "P3", "P4"
# ]

# # lista com os 3 voluntários que vamos converter
# voluntarios = ["S001", "S002", "S003"]

# # repete o processo pra cada voluntário da lista
# for pessoa in voluntarios:

#     # monta o nome do arquivo de entrada, baseado no voluntário atual
#     nome_entrada = pessoa + "R04.edf"

#     # abre o arquivo .edf original
#     arquivo = pyedflib.EdfReader(nome_entrada)

#     # pega a lista de TODOS os nomes de canais desse arquivo (64 no total)
#     nomes_canais_arquivo = arquivo.getSignalLabels()

#     # cria uma lista vazia, pra guardar os 16 canais que vamos extrair
#     dados_16_canais = []

#     # procura, um por um, os 16 eletrodos que realmente queremos
#     for nome_eletrodo in nomes_eletrodos:

#         # cria uma versão "limpa" dos nomes dos canais do arquivo, removendo os pontos extras
#         nomes_canais_limpos = [nome.strip(".") for nome in nomes_canais_arquivo]

#         # agora procura pelo nome limpo, sem se preocupar com quantos pontos tinha
#         indice = nomes_canais_limpos.index(nome_eletrodo)

#         # lê o sinal desse canal específico
#         sinal = arquivo.readSignal(indice)

#         # adiciona esse sinal na lista dos 16 canais
#         dados_16_canais.append(sinal)

#     # transforma a lista em um array do numpy, no formato (16 canais, amostras)
#     dados_finais = np.array(dados_16_canais)

#     # monta o nome do arquivo de saída pros dados do EEG
#     nome_saida_eeg = "gravacao_mu_" + pessoa + ".csv"

#     # salva os dados, separados por vírgula, num arquivo de texto simples
#     np.savetxt(nome_saida_eeg, dados_finais, delimiter=",")

#     print(f"Gravação convertida: {nome_saida_eeg}")

#     # pega as anotações do arquivo (momento de início, duração, texto do evento)
#     inicios, duracoes, textos = arquivo.readAnnotations()

#     # monta o nome do arquivo de saída pras anotações
#     nome_saida_anotacoes = "anotacoes_" + pessoa + ".txt"

#     # abre um arquivo novo, em modo escrita, pra salvar as anotações
#     with open(nome_saida_anotacoes, "w") as f:

#         # percorre cada anotação, juntando o momento (inicio) com o texto (T0/T1/T2)
#         for inicio, texto in zip(inicios, textos):

#             # escreve uma linha, com o momento e o texto separados por TAB
#             f.write(f"{inicio}\t{texto}\n")

#     print(f"Anotações salvas: {nome_saida_anotacoes}")

#     # fecha o arquivo original, liberando a memória
#     arquivo.close()