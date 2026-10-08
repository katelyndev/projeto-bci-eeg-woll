# Vai até a biblioteca BrainFlow e pega duas ferramentas
# DataFilter - onde ficam as funções de ler arquivo e filtrar
# FilterTypes - uma lista de tipos de filtro matemático que podemos escolher
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

# Ferramenta de gráficos visuais do Python
import matplotlib.pyplot as plt

# Abre o arquivo gravacao_ruido.csv e guarda todo o conteúdo dele
# (array completo: cada linha é um canal diferente)
dados = DataFilter.read_file('gravacao_ruido.csv')

# pega só uma linha desse array inteiro
# esse será o sinal "puro", que vamos preservar sem mexer
canal_original = dados[3]

# Remove o Offset DC de todo o canal antes de criar as cópias
DataFilter.detrend(canal_original, DetrendOperations.CONSTANT.value)

# TESTE 1: FILTRO PASSA-BAIXA
# cria uma cópia independente do sinal original
# isso evita que o filtro de baixo estrague o canal_original
teste_passa_baixa = canal_original.copy()

# aplica o filtro Passa-Baixa na cópia
# deixa passar só frequência baixa, corta tudo acima de 30Hz
# parâmetros: (sinal, taxa de amostragem, frequência de corte, ordem, tipo matemático, ripple)
DataFilter.perform_lowpass(teste_passa_baixa, 125, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 2: FILTRO PASSA-ALTA
# cria outra cópia nova, partindo do original intacto (não da cópia anterior)
teste_passa_alta = canal_original.copy()

# aplica o filtro Passa-Alta nessa cópia
# deixa passar só frequência alta, corta tudo abaixo de 8Hz
DataFilter.perform_highpass(teste_passa_alta, 125, 8, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 3: FILTRO PASSA-BANDA
# mais uma cópia nova, também a partir do original
teste_passa_banda = canal_original.copy()

# aplica o filtro Passa-Banda nessa cópia
# deixa passar só a faixa do meio (8Hz até 30Hz) - onde fica Mu/Beta
# parâmetros: (sinal, taxa de amostragem, frequência central, largura da banda, ordem, tipo, ripple)
DataFilter.perform_bandpass(teste_passa_banda, 125, 19.0, 22.0, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 4: FILTRO NOTCH
# última cópia nova, também partindo do original
teste_notch = canal_original.copy()

# aplica o filtro Notch nessa cópia
# remove só uma frequência específica (60Hz, da rede elétrica)
# parâmetros: (sinal, taxa de amostragem, frequência

# parâmetros: (sinal, taxa de amostragem, frequência a remover, largura da faixa removida, ordem, tipo, ripple)
DataFilter.perform_bandstop(teste_notch, 125, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 5: PIPELINE COMPLETO (Sinal Limpo Final)
# cria uma cópia que vai receber TODOS os filtros em sequência
sinal_limpo = canal_original.copy()

# 1. Remove a tendência / Offset DC
DataFilter.detrend(sinal_limpo, DetrendOperations.CONSTANT.value)

# 2. Remove o ruído de 60Hz da rede elétrica
DataFilter.perform_bandstop(sinal_limpo, 125, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# 3. Isola a faixa motora (8 a 30 Hz)
DataFilter.perform_bandpass(sinal_limpo, 125, 19.0, 22.0, 4, FilterTypes.BUTTERWORTH.value, 0)

# mostra os 5 primeiros valores de cada versão, só pra conferir rapidamente
print("Original:", canal_original[:5])
print("Passa-Baixa:", teste_passa_baixa[:5])
print("Passa-Alta:", teste_passa_alta[:5])
print("Passa-Banda:", teste_passa_banda[:5])
print("Notch:", teste_notch[:5])
print("Sinal Limpo:", sinal_limpo[:5])

# =====================================================================
# VISUALIZAÇÃO GRÁFICA COM MATPLOTLIB
# =====================================================================

# Cria uma figura contendo 2 gráficos empilhados (2 linhas, 1 coluna)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)

# GRÁFICO 1 (SUPERIOR): Sinal Bruto com Ruído
ax1.plot(canal_original, color='crimson', alpha=0.8, label='Sinal Bruto (Canal 4)')
ax1.set_title('EEG Bruto - Sem Tratamento (Com Offset DC e Ruído Elétrico)')
ax1.set_ylabel(r'Amplitude ($\mu V$)')
ax1.legend(loc='upper right')
ax1.grid(True)

# GRÁFICO 2 (INFERIOR): Sinal Filtrado Limpo
ax2.plot(sinal_limpo, color='teal', label='Sinal Filtrado (Detrend + Notch 60Hz + Bandpass 8-30Hz)')
ax2.set_title('EEG Processado - Sinal Limpo (Pronto para Controle Motor)')
ax2.set_xlabel('Número de Amostras')
ax2.set_ylabel(r'Amplitude ($\mu V$)')
ax2.legend(loc='upper right')
ax2.grid(True)

# Ajusta os espaçamentos e exibe a janela na tela
plt.tight_layout()
plt.show()