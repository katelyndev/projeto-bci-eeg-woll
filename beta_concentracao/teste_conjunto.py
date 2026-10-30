# TESTE CONJUNTO: junta tudo numa rodada só, nas 6 gravações
#  1) descarta pedaços (janelas) com ruído forte
#  2) calcula o Engagement Index (NASA) e a Beta e a Alfa em cada pedaço
#  3) compara o FOCO com o RELAX da MESMA pessoa, usando Z-score
# Não decide "concentrado ou não": só mostra se subiu ou desceu.

# traz o Path, pra descobrir a pasta onde este script está salvo
from pathlib import Path
# traz o numpy, ferramenta de cálculo (média, desvio padrão, etc.)
import numpy as np
# traz o DataFilter, que sabe ler os CSVs no formato do BrainFlow
from brainflow.data_filter import DataFilter
# reaproveita a função do Pedro: ela devolve as frequências, a PSD e a Beta (13-30 Hz)
from analise_beta import calcular_beta

# ---------------------------------------------------------------
# CONFIGURAÇÕES 
# ---------------------------------------------------------------

# lista das gravações que vamos testar (pessoa + sessão)
GRAVACOES = ["S001E01", "S001E02", "S002E01", "S002E02", "S003E01", "S003E02"]
# taxa de amostragem desse dataset (EMOTIV EPOC+)
FS = 256
# posição do canal F3 na lista de 14 canais (contando a partir do zero)
CANAL = 2
# tamanho de cada janela, em segundos
JANELA_SEGUNDOS = 4
# limite de "pico a pico" (maior valor menos menor valor) da janela;
# acima disso a janela é considerada ruído forte e é descartada
# (300 é um valor escolhido por nós para testar, não vem de nenhum estudo)
LIMITE_PICO_A_PICO = 100000

# descobre em qual pasta este script está salvo
PASTA = Path(__file__).resolve().parent


# ---------------------------------------------------------------
# FUNÇÕES
# ---------------------------------------------------------------

# soma a potência de uma faixa de frequência, a partir da PSD já calculada
def potencia_da_faixa(frequencias, psd, minimo, maximo):
    # marca quais frequências estão dentro da faixa pedida
    faixa = (frequencias >= minimo) & (frequencias <= maximo)
    # integra (soma) a PSD só nessa faixa e devolve o resultado
    return np.trapezoid(psd[faixa], frequencias[faixa])


# lê um trecho (relax1 ou foco) e devolve as medidas de cada janela válida
def medidas_do_trecho(pessoa, trecho):
    # monta o caminho do arquivo CSV desse trecho
    caminho = PASTA / f"gravacao_concentracao_{trecho}_{pessoa}.csv"
    # lê o arquivo inteiro
    dados = DataFilter.read_file(str(caminho))
    # pega só a linha do canal F3
    sinal = dados[CANAL]
    # calcula quantas amostras cabem em uma janela
    tamanho = int(JANELA_SEGUNDOS * FS)

    # listas vazias, uma pra cada medida
    betas, engajamentos, alfas = [], [], []
    # contador de janelas descartadas por ruído
    descartadas = 0
    # contador de janelas lidas no total
    total = 0

    # percorre o sinal, pulando de janela em janela
    for inicio in range(0, len(sinal), tamanho):
        # pega o pedaço desta janela
        pedaco = sinal[inicio:inicio + tamanho]
        # se o último pedaço for menor que uma janela completa, para
        if len(pedaco) < tamanho:
            break
        # conta mais uma janela lida
        total += 1
        # tira o valor médio do pedaço (assim o "pico a pico" não depende do nível base)
        pedaco = pedaco - np.mean(pedaco)
        # calcula o pico a pico: maior valor menos menor valor
        pico_a_pico = np.max(pedaco) - np.min(pedaco)
        # se passou do limite, é ruído forte: descarta e vai pra próxima janela
        if pico_a_pico > LIMITE_PICO_A_PICO:
            descartadas += 1
            continue

        # reaproveita a função do Pedro: frequências, PSD e Beta (13-30 Hz)
        frequencias, psd, beta = calcular_beta(pedaco, FS)
        # Theta (4-8 Hz), usado na conta da NASA
        theta = potencia_da_faixa(frequencias, psd, 4, 8)
        # Alfa (8-13 Hz), usada na conta da NASA e no teste da Alfa
        alfa = potencia_da_faixa(frequencias, psd, 8, 13)
        # Beta na faixa da NASA (13-22 Hz)
        beta_nasa = potencia_da_faixa(frequencias, psd, 13, 22)
        # Engagement Index = Beta / (Alfa + Theta)
        engajamento = beta_nasa / (alfa + theta)

        # guarda os resultados desta janela nas listas
        betas.append(beta)
        engajamentos.append(engajamento)
        alfas.append(alfa)

    # devolve tudo, em forma de dicionário
    return {
        "beta": np.array(betas),
        "engajamento": np.array(engajamentos),
        "alfa": np.array(alfas),
        "descartadas": descartadas,
        "total": total,
    }


# calcula a média dos Z-scores do foco, usando o relax como "normal da pessoa"
def media_zscore(valores_relax, valores_foco):
    # média do relax: o "normal" da pessoa
    media = np.mean(valores_relax)
    # desvio padrão do relax: a variação natural da pessoa
    desvio = np.std(valores_relax)
    # se não houver variação, não dá pra calcular o Z-score
    if desvio == 0:
        return float("nan")
    # Z-score de cada janela do foco, e a média deles
    return float(np.mean((valores_foco - media) / desvio))


# traduz o sinal de um número em palavras
def direcao(numero):
    # se não foi possível calcular, avisa
    if np.isnan(numero):
        return "sem dado"
    # positivo: subiu no foco
    if numero > 0:
        return "SUBIU no foco"
    # zero ou negativo: desceu (ou ficou igual)
    return "DESCEU no foco"


# ---------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------------

# lista que guarda uma linha de resumo por gravação
resumo = []

# repete o teste para cada gravação
for pessoa in GRAVACOES:
    # mede as janelas do relax1 e do foco
    relax = medidas_do_trecho(pessoa, "relax1")
    foco = medidas_do_trecho(pessoa, "foco")

    # mostra o cabeçalho desta gravação
    print(f"\n===== {pessoa} =====")
    # mostra quantas janelas foram descartadas por ruído em cada trecho
    print(f"Janelas descartadas por ruído: relax1 {relax['descartadas']}/{relax['total']} | foco {foco['descartadas']}/{foco['total']}")

    # precisamos de pelo menos 2 janelas boas no relax e 1 no foco
    if len(relax["beta"]) < 2 or len(foco["beta"]) < 1:
        # avisa e passa pra próxima gravação
        print("Poucas janelas boas: não deu pra calcular.")
        continue

    # média do Engagement Index no relax e no foco
    ei_relax = float(np.mean(relax["engajamento"]))
    ei_foco = float(np.mean(foco["engajamento"]))
    # Z-score médio da Beta, do Engagement Index e da Alfa
    z_beta = media_zscore(relax["beta"], foco["beta"])
    z_ei = media_zscore(relax["engajamento"], foco["engajamento"])
    z_alfa = media_zscore(relax["alfa"], foco["alfa"])

    # mostra o Engagement Index (foco menos relax)
    print(f"Engagement Index: relax {ei_relax:.4f} | foco {ei_foco:.4f} | diferença {ei_foco - ei_relax:+.4f}")
    # mostra o Z-score médio de cada medida, com a direção em palavras
    print(f"Z-score médio Beta:        {z_beta:+.2f}  ({direcao(z_beta)})")
    print(f"Z-score médio Engagement:  {z_ei:+.2f}  ({direcao(z_ei)})")
    print(f"Z-score médio Alfa:        {z_alfa:+.2f}  ({direcao(z_alfa)})")

    # guarda a linha de resumo desta gravação
    resumo.append((pessoa, z_beta, z_ei, z_alfa))

# tabela final, com as gravações lado a lado
print("\n===== RESUMO (Z-score médio do foco contra o relax da mesma pessoa) =====")
# cabeçalho da tabela
print(f"{'Gravação':<10}{'Beta':>8}{'Engagement':>12}{'Alfa':>8}")
# uma linha por gravação
for pessoa, z_beta, z_ei, z_alfa in resumo:
    print(f"{pessoa:<10}{z_beta:>+8.2f}{z_ei:>+12.2f}{z_alfa:>+8.2f}")
# aviso final: poucos dados, é só indício
print("\nLembrete: são poucas pessoas e não sabemos se elas realmente se concentraram. Isto é indício, não prova.")
