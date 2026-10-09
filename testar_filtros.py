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

# pega só uma linha desse array inteiro
# esse será o sinal "puro", que vamos preservar sem mexer
canal_original = dados[3]

# Remove o Offset DC de todo o canal antes de criar as cópias
DataFilter.detrend(canal_original, DetrendOperations.CONSTANT.value)

# TESTE 1: FILTRO PASSA-BAIXA
teste_passa_baixa = canal_original.copy()
DataFilter.perform_lowpass(teste_passa_baixa, 125, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 2: FILTRO PASSA-ALTA
teste_passa_alta = canal_original.copy()
DataFilter.perform_highpass(teste_passa_alta, 125, 8, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 3: FILTRO PASSA-BANDA
teste_passa_banda = canal_original.copy()
DataFilter.perform_bandpass(teste_passa_banda, 125, 8, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 4: FILTRO NOTCH
teste_notch = canal_original.copy()
DataFilter.perform_bandstop(teste_notch, 125, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 5: PIPELINE COMPLETO (Sinal Limpo Final)
sinal_limpo = canal_original.copy()
DataFilter.perform_bandstop(sinal_limpo, 125, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)
DataFilter.perform_bandpass(sinal_limpo, 125, 8, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

print("Original:", canal_original[:5])
print("Passa-Baixa:", teste_passa_baixa[:5])
print("Passa-Alta:", teste_passa_alta[:5])
print("Passa-Banda:", teste_passa_banda[:5])
print("Notch:", teste_notch[:5])
print("Sinal Limpo:", sinal_limpo[:5])

# =====================================================================
# VISUALIZAÇÃO GRÁFICA COM MATPLOTLIB
# =====================================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)

ax1.plot(canal_original, color='crimson', alpha=0.8, label='Sinal Bruto (Canal 4)')
ax1.set_title('EEG Bruto - Sem Tratamento (Com Offset DC e Ruído Elétrico)')
ax1.set_ylabel(r'Amplitude ($\mu V$)')
ax1.legend(loc='upper right')
ax1.grid(True)

ax2.plot(sinal_limpo, color='teal', label='Sinal Filtrado (Detrend + Notch 60Hz + Bandpass 8-30Hz)')
ax2.set_title('EEG Processado - Sinal Limpo (Pronto para Controle Motor)')
ax2.set_xlabel('Número de Amostras')
ax2.set_ylabel(r'Amplitude ($\mu V$)')
ax2.legend(loc='upper right')
ax2.grid(True)

plt.tight_layout()
plt.show()

board_id = BoardIds.SYNTHETIC_BOARD.value  # ou o board correto usado na gravação
eeg_channels = BoardShim.get_eeg_channels(board_id)

# filtra SÓ os canais de EEG, preservando as outras linhas (timestamp, etc)
# CORRIGIDO: 19.0, 22.0 (centro/largura, versão do Pedro) → 8, 30 (start/stop, sua versão)
for canal in eeg_channels:
    DataFilter.detrend(dados[canal], DetrendOperations.CONSTANT.value)
    DataFilter.perform_bandstop(dados[canal], 125, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)
    DataFilter.perform_bandpass(dados[canal], 125, 8, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

DataFilter.write_file(dados, 'gravacao_filtrada.csv', 'w')

# # pega todas as linhas (todos os canais), mas só as primeiras 1000 colunas
# # isso corta o sinal em um pedaço menor (cerca de 8 segundos, já que fs=125)
# # o objetivo é reduzir o tamanho do arquivo final, pra testar se isso resolve
# # a instabilidade do Streaming Board com arquivos grandes
# dados_reduzidos = dados[:, :1000].copy()

# # repete o filtro Passa-Banda, só que agora na versão reduzida do sinal
# # continua filtrando só os canais de EEG de verdade (eeg_channels),
# # igual fizemos antes, pra não estragar as linhas de contagem/metadado
# for canal in eeg_channels:
#     DataFilter.perform_bandpass(dados_reduzidos[canal], 125, 8, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

# # salva essa versão reduzida e já filtrada num arquivo novo, menor que o anterior
# DataFilter.write_file(dados_reduzidos, 'gravacao_filtrada_pequena.csv', 'w')

# # avisa na tela que deu tudo certo
# print("Arquivo filtrado reduzido salvo com sucesso!")