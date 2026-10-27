# Conversor pro novo dataset de concentração (EEG Dataset of Fusion
# Relaxation and Concentration Moods - Mendeley)
#
# Formato de origem: .edf, 14 canais (EMOTIV EPOC+), 256 Hz
# Canais: AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4
#
# Estrutura de cada gravação (3 minutos = 180 segundos):
#   minuto 1 (0-60s)   -> relaxamento (baseline)
#   minuto 2 (60-120s) -> concentração (resolvendo problema)
#   minuto 3 (120-180s)-> relaxamento de novo

# traz a ferramenta que sabe ler arquivos .edf
import pyedflib

# traz o numpy, pra organizar os números
import numpy as np

# traz o DataFilter, pra salvar no formato que o resto do projeto usa
from brainflow.data_filter import DataFilter

# lista com os códigos das pessoas que vamos converter (ajuste conforme baixado)
pessoas = ["S001E01", "S002E01", "S003E01", "S001E02", "S002E02", "S003E02"]

# repete o processo pra cada pessoa da lista
for pessoa in pessoas:

    # monta o nome do arquivo de entrada
    nome_entrada = pessoa + ".edf"

    # abre o arquivo .edf
    arquivo = pyedflib.EdfReader(nome_entrada)

    # pega os nomes reais dos 14 canais desse arquivo, só pra conferência
    nomes_canais = arquivo.getSignalLabels()
    print(f"\n{pessoa} - Canais encontrados: {nomes_canais}")

    # pega a taxa de amostragem real (deve ser 256Hz)
    fs_real = arquivo.getSampleFrequency(0)
    print(f"Taxa de amostragem: {fs_real} Hz")

    # lê o sinal de TODOS os 14 canais
    num_canais = len(nomes_canais)
    sinais = [arquivo.readSignal(i) for i in range(num_canais)]

    # fecha o arquivo original
    arquivo.close()

    # transforma a lista em array numpy, formato (14 canais, amostras)
    dados_completos = np.array(sinais)

    # descobre quantas amostras tem, no total
    total_amostras = dados_completos.shape[1]
    print(f"Total de amostras: {total_amostras} ({total_amostras/fs_real:.1f} segundos)")

    # calcula em que amostra começa e termina cada "minuto" da gravação
    amostras_por_minuto = int(60 * fs_real)

    # minuto 1: relaxamento (baseline)
    relaxamento_1 = np.ascontiguousarray(dados_completos[:, 0:amostras_por_minuto])

    # minuto 2: concentração (resolvendo problema)
    concentracao = np.ascontiguousarray(dados_completos[:, amostras_por_minuto:amostras_por_minuto*2])

    # minuto 3: relaxamento de novo
    relaxamento_2 = np.ascontiguousarray(dados_completos[:, amostras_por_minuto*2:amostras_por_minuto*3])

    # salva cada trecho separadamente, no formato do BrainFlow
    DataFilter.write_file(relaxamento_1, f"gravacao_concentracao_relax1_{pessoa}.csv", "w")
    DataFilter.write_file(concentracao, f"gravacao_concentracao_foco_{pessoa}.csv", "w")
    DataFilter.write_file(relaxamento_2, f"gravacao_concentracao_relax2_{pessoa}.csv", "w")

    print(f"Convertido: {pessoa} -> 3 arquivos separados (relax1, foco, relax2)")
