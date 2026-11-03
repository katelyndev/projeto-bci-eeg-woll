# INSPECIONAR JANELAS: mostra, janela por janela, quanto o sinal oscila (pico a pico)
# e separa o que é "deriva lenta" do que é "ruído rápido".
# Objetivo: entender por que algumas janelas foram descartadas no teste_conjunto.py.

# traz o Path, pra descobrir a pasta onde este script está salvo
from pathlib import Path
# traz o numpy, ferramenta de cálculo com listas de números
import numpy as np
# traz o DataFilter, que sabe ler os CSVs no formato do BrainFlow
from brainflow.data_filter import DataFilter
# traz duas ferramentas de filtro do scipy: criar o filtro (butter) e aplicá-lo (sosfiltfilt)
from scipy.signal import butter, sosfiltfilt

# ---------------------------------------------------------------
# CONFIGURAÇÕES 
# ---------------------------------------------------------------

# qual gravação vamos inspecionar nesta rodada
SESSAO = "S003E01"
# taxa de amostragem do dataset de concentração (EMOTIV): 256 pontos por segundo
FS = 256
# posição do canal F3 na lista de 14 canais (contando a partir do zero)
CANAL = 2
# tamanho de cada janela, em segundos
JANELA_SEGUNDOS = 4
# limite de pico a pico (em µV); o mesmo 300 do teste_conjunto.py, pra comparar de forma justa
LIMITE_PICO_A_PICO = 300
# frequência de corte do filtro que tira a parte lenta (abaixo de 1 Hz)
CORTE_LENTO_HZ = 1

# descobre em qual pasta este script está salvo
PASTA = Path(__file__).resolve().parent

# mostra na tela um resumo da configuração, só pra confirmar que está tudo certo
print(f"Gravação: {SESSAO} | FS: {FS} Hz | Limite: {LIMITE_PICO_A_PICO} µV | Corte lento: {CORTE_LENTO_HZ} Hz")

# ---------------------------------------------------------------
# FUNÇÕES
# ---------------------------------------------------------------

# lê um trecho (relax1 ou foco) de uma sessão e devolve só o sinal do canal F3
def ler_sinal(trecho, sessao):
    # monta o caminho do arquivo CSV, usando o trecho e a sessão recebidos
    caminho = PASTA / f"gravacao_concentracao_{trecho}_{sessao}.csv"
    # lê o arquivo inteiro (14 linhas, uma por canal)
    dados = DataFilter.read_file(str(caminho))
    # pega só a linha do canal F3 e garante que são números decimais
    sinal = np.asarray(dados[CANAL], dtype=float)
    # devolve o sinal, pra quem chamou a função usar
    return sinal


# recebe um sinal e devolve uma cópia dele sem a parte lenta (abaixo de 1 Hz)
def tirar_parte_lenta(sinal):
    # tira o valor médio do sinal, pra o filtro não ter um "tranco" no começo
    sinal = sinal - np.mean(sinal)
    # cria um filtro "passa-alta": deixa passar o que é mais rápido que 1 Hz e corta o que é mais lento
    filtro = butter(4, CORTE_LENTO_HZ, btype="highpass", fs=FS, output="sos")
    # aplica o filtro no sinal inteiro e devolve o resultado
    return sosfiltfilt(filtro, sinal)


# recebe o sinal inteiro de um trecho e devolve uma lista com as medidas de cada janela de 4 s
def medir_janelas(sinal):
    # cria a versão do sinal sem a parte lenta (filtrando o trecho inteiro, de uma vez)
    sem_lenta = tirar_parte_lenta(sinal)
    # calcula quantos pontos cabem em uma janela (4 s x 256 pontos = 1024)
    tamanho = int(JANELA_SEGUNDOS * FS)
    # cria uma lista vazia, pra guardar o resultado de cada janela
    janelas = []

    # percorre o sinal pulando de 1024 em 1024 pontos; só começa janelas que cabem inteiras
    for inicio in range(0, len(sinal) - tamanho + 1, tamanho):
        # pega o pedaço do sinal original desta janela
        pedaco = sinal[inicio:inicio + tamanho]
        # pega o pedaço correspondente do sinal sem a parte lenta
        pedaco_sem_lenta = sem_lenta[inicio:inicio + tamanho]
        # mede o pico a pico do original (maior valor menos menor valor)
        pp_original = float(np.ptp(pedaco))
        # mede o pico a pico do sinal sem a parte lenta
        pp_sem_lenta = float(np.ptp(pedaco_sem_lenta))
        # guarda as medidas desta janela, junto com o tempo em que ela começa
        janelas.append({
            "tempo": inicio / FS,
            "pp_original": pp_original,
            "pp_sem_lenta": pp_sem_lenta,
        })

    # devolve a lista completa, com todas as janelas
    return janelas


# lista com as 6 gravações que vamos classificar
SESSOES = ["S001E01", "S001E02", "S002E01", "S002E02", "S003E01", "S003E02"]


# recebe os números de UMA janela e diz se ela é normal, deriva lenta ou ruído rápido
def classificar(janela):
    # se o pico a pico original não passa do limite, a janela é normal
    if janela["pp_original"] <= LIMITE_PICO_A_PICO:
        return "normal"
    # passou do limite; se sem a parte lenta ele cai abaixo, era só deriva lenta
    if janela["pp_sem_lenta"] <= LIMITE_PICO_A_PICO:
        return "deriva lenta"
    # passou do limite nos dois casos: é um evento rápido e forte
    return "ruído rápido"


# contadores do total geral (começam em zero)
total = {"normal": 0, "deriva lenta": 0, "ruído rápido": 0}

# repete para cada uma das 6 gravações
for sessao in SESSOES:
    # e, dentro de cada gravação, para os dois trechos
    for trecho in ["relax1", "foco"]:
        # mede todas as janelas desse trecho
        janelas = medir_janelas(ler_sinal(trecho, sessao))
        # classifica cada janela, guardando o resultado numa lista
        classes = [classificar(j) for j in janelas]
        # soma o que encontrou no total geral
        for c in classes:
            total[c] += 1
        # descobre em que segundo começam as janelas de ruído rápido
        tempos_rapidos = [int(j["tempo"]) for j, c in zip(janelas, classes) if c == "ruído rápido"]
        # mostra uma linha de resumo para este trecho
        print(f"{sessao} | {trecho:6s} | normal {classes.count('normal'):2d} | deriva lenta {classes.count('deriva lenta'):2d} | ruído rápido {classes.count('ruído rápido'):2d} | rápidos em (s): {tempos_rapidos}")

# mostra o total das 6 gravações
print(f"\nTOTAL | normal {total['normal']} | deriva lenta {total['deriva lenta']} | ruído rápido {total['ruído rápido']}")