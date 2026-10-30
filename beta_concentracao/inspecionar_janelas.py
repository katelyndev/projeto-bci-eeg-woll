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

# lê um trecho da gravação (relax1 ou foco) e devolve só o sinal do canal F3
def ler_sinal(trecho):
    # monta o caminho do arquivo CSV desse trecho, usando o nome da sessão
    caminho = PASTA / f"gravacao_concentracao_{trecho}_{SESSAO}.csv"
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


# ---------------------------------------------------------------
# TESTE TEMPORÁRIO (vamos apagar quando fizermos o bloco 4)
# ---------------------------------------------------------------

# repete para os dois trechos da sessão: primeiro o relax1, depois o foco
for trecho in ["relax1", "foco"]:
    # imprime um título, pra separar visualmente cada trecho
    print(f"\n--- {SESSAO} | {trecho} ---")
    # mede as janelas desse trecho e percorre uma por uma, com o número (começando em 1)
    for numero, j in enumerate(medir_janelas(ler_sinal(trecho)), start=1):
        # se o pico a pico original passou do limite, cria um aviso; senão, deixa em branco
        marca = "  <-- acima do limite" if j["pp_original"] > LIMITE_PICO_A_PICO else ""
        # mostra a linha da janela, com o aviso no final quando houver
        print(f"Janela {numero:2d} | {j['tempo']:5.1f} s | original {j['pp_original']:7.1f} | sem parte lenta {j['pp_sem_lenta']:7.1f}{marca}")