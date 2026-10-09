# Vai até a biblioteca BrainFlow e pega duas ferramentas
# DataFilter - onde ficam as funções de ler arquivo e filtrar
# FilterTypes - uma lista de tipos de filtro matemático que podemos escolher
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

from brainflow.board_shim import BoardShim, BoardIds

# Ferramenta de gráficos visuais do Python
import matplotlib.pyplot as plt

# Abre o arquivo gravacao_ruido.csv e guarda todo o conteúdo dele
# (array completo: cada linha é um canal diferente)
dados = DataFilter.read_file('gravacao_ruido.csv')

frequencia_amostragem = 160


# pega só uma linha desse array inteiro
# Guarda uma cópia do sinal bruto, sem modificações
canal_original = dados[3].copy()

# Cria outra cópia para realizar o processamento
canal_processamento = canal_original.copy()

# Remove o offset DC somente da cópia de processamento
DataFilter.detrend(canal_processamento, DetrendOperations.CONSTANT.value)

# TESTE 1: FILTRO PASSA-BAIXA
# cria uma cópia independente do sinal original
# isso evita que o filtro de baixo estrague o canal_original
teste_passa_baixa = canal_processamento.copy()

# aplica o filtro Passa-Baixa na cópia
# deixa passar só frequência baixa, corta tudo acima de 30Hz
# parâmetros: (sinal, taxa de amostragem, frequência de corte, ordem, tipo matemático, ripple)
DataFilter.perform_lowpass(teste_passa_baixa, frequencia_amostragem, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 2: FILTRO PASSA-ALTA
# cria outra cópia nova, partindo do original intacto (não da cópia anterior)
teste_passa_alta = canal_processamento.copy()

# aplica o filtro Passa-Alta nessa cópia
# deixa passar só frequência alta, corta tudo abaixo de 8Hz
DataFilter.perform_highpass(teste_passa_alta, frequencia_amostragem, 8, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 3: FILTRO PASSA-BANDA
# mais uma cópia nova, também a partir do original
teste_passa_banda = canal_processamento.copy()

# aplica o filtro Passa-Banda nessa cópia
# deixa passar só a faixa do meio (8Hz até 30Hz) - onde fica Mu/Beta
# parâmetros: (sinal, taxa de amostragem, frequência central, largura da banda, ordem, tipo, ripple)
DataFilter.perform_bandpass(teste_passa_banda, frequencia_amostragem, 19.0, 22.0, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 4: FILTRO NOTCH
# última cópia nova, também partindo do original
teste_notch = canal_processamento.copy()

# aplica o filtro Notch nessa cópia
# remove só uma frequência específica (60Hz, da rede elétrica)
# parâmetros: (sinal, taxa de amostragem, frequência

# parâmetros: (sinal, taxa de amostragem, frequência a remover, largura da faixa removida, ordem, tipo, ripple)
DataFilter.perform_bandstop(teste_notch, frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 5: PIPELINE COMPLETO (Sinal Limpo Final)
# cria uma cópia que vai receber TODOS os filtros em sequência
sinal_limpo = canal_processamento.copy()

# Remove o ruído de 60Hz da rede elétrica
DataFilter.perform_bandstop(sinal_limpo, frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# Isola a faixa motora (8 a 30 Hz)
DataFilter.perform_bandpass(sinal_limpo, frequencia_amostragem, 19.0, 22.0, 4, FilterTypes.BUTTERWORTH.value, 0)

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

board_id = BoardIds.SYNTHETIC_BOARD.value  # ou o board correto usado na gravação
eeg_channels = BoardShim.get_eeg_channels(board_id)

# pega todas as linhas (todos os canais), mas só as primeiras 1000 colunas
# 1000 amostras correspondem a 1000 / frequencia_amostragem segundos
# o objetivo é reduzir o tamanho do arquivo final, pra testar se isso resolve
# a instabilidade do Streaming Board com arquivos grandes
dados_reduzidos = dados[:, :1000].copy()

# repete o filtro Passa-Banda, só que agora na versão reduzida do sinal
# continua filtrando só os canais de EEG de verdade (eeg_channels),
# igual fizemos antes, pra não estragar as linhas de contagem/metadado
for canal in eeg_channels:
    DataFilter.detrend(dados_reduzidos[canal], DetrendOperations.CONSTANT.value)
    DataFilter.perform_bandstop(dados_reduzidos[canal], frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)
    DataFilter.perform_bandpass(dados_reduzidos[canal], frequencia_amostragem, 19.0, 22.0, 4, FilterTypes.BUTTERWORTH.value, 0)

# salva essa versão reduzida e já filtrada num arquivo novo, menor que o anterior
DataFilter.write_file(dados_reduzidos, 'gravacao_filtrada_pequena.csv', 'w')

# avisa na tela que deu tudo certo
print("Arquivo filtrado reduzido salvo com sucesso!")