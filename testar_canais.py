# # traz o numpy, ferramenta pra trabalhar com números e listas de forma eficiente
# import numpy as np

# # traz a função welch, que calcula a força de cada frequência dentro de um sinal
# from scipy.signal import welch

# # traz o DataFilter, ferramenta do BrainFlow pra ler os arquivos CSV
# # from brainflow.data_filter import DataFilter

# import pyedflib

# # define a função que calcula a potência de UMA faixa de frequência específica
# # ela recebe: o nome do arquivo, qual canal usar, o início e fim da faixa, 
# # um nome pra identificar a faixa no print, e a taxa de amostragem (fixa em 160)
# def calcular_potencia_banda(nome_arquivo, indice_canal, freq_min, freq_max, nome_banda, fs=160):

#     # # lê o arquivo CSV inteiro e guarda o conteúdo numa variável
#     # dados = DataFilter.read_file(nome_arquivo)

#     # # pega só a linha do canal que escolhemos (ex: canal O1)
#     # canal = dados[indice_canal]

#     #  abre o arquivo .edf, preparando para ser lido
#     arquivo = pyedflib.EdfReader(nome_arquivo)

#     # pega do arquivo o sinal do canal excolhido
#     canal = arquivo.readSignal(indice_canal)
#     # pergunta para o arquivo qual a taxa de amostragem real do canal 
#     fs = arquivo.getSampleFrequency(indice_canal)
#     # fecha o arquivo avisando que j erminamos de usar ele 
#     arquivo.close()


#     # calcula a força de cada frequência presente nesse canal
#     freqs, psd = welch(canal, fs=fs)

#     # descobre quais posições da lista de frequências estão DENTRO da faixa pedida
#     indices_banda = np.where((freqs >= freq_min) & (freqs <= freq_max))[0]

#     # calcula a média da força, só das posições que estão dentro da faixa
#     potencia_banda = np.mean(psd[indices_banda])

#     # mostra na tela o resultado, já identificando arquivo, faixa e banda
#     print(f"Arquivo: {nome_arquivo} | Banda {nome_banda} ({freq_min}-{freq_max}Hz) | Potência: {potencia_banda:.2f}")

#     # devolve o valor calculado, caso alguém queira usar depois
#     return potencia_banda

# calcular_potencia_banda('Subject00_1.edf', 0, 13, 30, "Beta")

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

# traz o numpy
import numpy as np

# traz a ferramenta "os", que ajuda a lidar com caminhos de arquivo
import os

# traz o DataFilter
from brainflow.data_filter import DataFilter

# taxa de amostragem desse dataset
fs = 250

# caminho da pasta onde estão os arquivos .txt originais
pasta = "dataset_cognitive_load/raw_data/Arithmetic_Data/"

# lista com os nomes dos arquivos que queremos converter, já com o caminho completo
arquivos_para_converter = [
    pasta + "natural-1.txt", pasta + "highlevel-1.txt",
    pasta + "natural-2.txt", pasta + "highlevel-2.txt",
    pasta + "natural-3.txt", pasta + "highlevel-3.txt"
]
# repete o processo de conversão, uma vez pra cada arquivo da lista
for nome_arquivo in arquivos_para_converter:

    # lê o arquivo, pegando só as colunas 1 a 8 (os 8 canais de EEG)
    dados_brutos = np.loadtxt(nome_arquivo, delimiter=",", usecols=range(1, 9))

    # transpõe pro formato (canais, amostras)
    dados_brutos = dados_brutos.T

    # descobre quantas amostras tem
    total_amostras = dados_brutos.shape[1]

    # cria a linha de contador
    linha_contador = np.arange(total_amostras).reshape(1, -1)

    # cria a linha de timestamp
    linha_timestamp = (np.arange(total_amostras) / fs).reshape(1, -1)

    # junta tudo: contador + 8 canais + timestamp
    dados_finais = np.vstack([linha_contador, dados_brutos, linha_timestamp])

    # reorganiza a memória do array, garantindo o formato que o BrainFlow espera
    dados_finais = np.ascontiguousarray(dados_finais)

    # pega só o NOME do arquivo (sem a pasta na frente)
    nome_limpo = os.path.basename(nome_arquivo)

    # monta o nome de saída, usando só esse nome limpo
    nome_saida = "gravacao_beta_" + nome_limpo.replace(".txt", ".csv")

    # salva no formato do BrainFlow
    DataFilter.write_file(dados_finais, nome_saida, "w")

    print(f"Convertido: {nome_arquivo} → {nome_saida}") 