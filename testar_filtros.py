# # Vai até a biblioteca BrainFlow e pega duas ferramentas
# # DataFilter - onde ficam as funções de ler arquivo e filtrar
# # FilterTypes - uma lista de tipos de filtro matemático que podemos escolher
# from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

# # traz BoardShim e BoardIds, usados pra identificar informações sobre o board
# from brainflow.board_shim import BoardShim, BoardIds

# # Ferramenta de gráficos visuais do Python
# import matplotlib.pyplot as plt

# # Abre o arquivo gravacao_olhos_fechados.csv e guarda todo o conteúdo dele
# # (array completo: cada linha é um canal diferente)
# dados = DataFilter.read_file('gravacao_olhos_fechados.csv') # gravacao_ruido.csv gravacao_olhos_fechados.csv gravacao_olhos_abertos.csv

# # mostra na tela o TIPO da variável "dados" (confirma que é um array numpy)
# print("Tipo dos dados:", type(dados))

# # mostra na tela as DIMENSÕES do array (quantas linhas, quantas colunas)
# print("Dimensões dos dados:", dados.shape)

# # guarda a taxa de amostragem real (160Hz) numa variável, pra reutilizar depois
# frequencia_amostragem = 160

# # pega a linha correspondente ao canal O1 (posição 7), e faz uma cópia
# # essa cópia vai ficar intacta, representando o sinal "bruto" original
# canal_original = dados[7].copy()

# # cria outra cópia, que vai ser usada pra fazer o processamento/filtros
# canal_processamento = canal_original.copy()

# # remove o offset DC (um desvio constante) somente da cópia de processamento
# DataFilter.detrend(canal_processamento, DetrendOperations.CONSTANT.value)

# # TESTE 1: FILTRO PASSA-BAIXA
# # cria uma cópia independente, partindo do sinal já sem offset DC
# teste_passa_baixa = canal_processamento.copy()

# # aplica o filtro Passa-Baixa: deixa passar só frequência baixa, corta acima de 30Hz
# # parâmetros: (sinal, taxa de amostragem, frequência de corte, ordem, tipo matemático, ripple)
# DataFilter.perform_lowpass(teste_passa_baixa, frequencia_amostragem, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

# # TESTE 2: FILTRO PASSA-ALTA
# # cria outra cópia nova, partindo do processamento (não da cópia anterior)
# teste_passa_alta = canal_processamento.copy()

# # aplica o filtro Passa-Alta: deixa passar só frequência alta, corta abaixo de 8Hz
# DataFilter.perform_highpass(teste_passa_alta, frequencia_amostragem, 8, 4, FilterTypes.BUTTERWORTH.value, 0)

# # TESTE 3: FILTRO PASSA-BANDA
# # mais uma cópia nova, também a partir do processamento
# teste_passa_banda = canal_processamento.copy()

# # aplica o filtro Passa-Banda: deixa passar só 8-13Hz (faixa da Alfa)
# # parâmetros: (sinal, taxa de amostragem, início da faixa, fim da faixa, ordem, tipo, ripple)
# DataFilter.perform_bandpass(teste_passa_banda, frequencia_amostragem, 8, 13, 4, FilterTypes.BUTTERWORTH.value, 0)

# # TESTE 4: FILTRO NOTCH
# # última cópia nova, também partindo do processamento
# teste_notch = canal_processamento.copy()

# # aplica o filtro Notch: remove só a faixa de 58-62Hz (interferência elétrica)
# # parâmetros: (sinal, taxa de amostragem, início da faixa a remover, fim da faixa, ordem, tipo, ripple)
# DataFilter.perform_bandstop(teste_notch, frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# # TESTE 5: PIPELINE COMPLETO (Sinal Limpo Final)
# # cria uma cópia que vai receber TODOS os filtros em sequência
# sinal_limpo = canal_processamento.copy()

# # remove o ruído de 60Hz da rede elétrica
# DataFilter.perform_bandstop(sinal_limpo, frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# # isola a faixa da Alfa (8 a 13Hz)
# DataFilter.perform_bandpass(sinal_limpo, frequencia_amostragem, 8, 13, 4, FilterTypes.BUTTERWORTH.value, 0)

# # mostra os 5 primeiros valores do sinal original, sem filtro nenhum
# print("Original:", canal_original[:5])

# # mostra os 5 primeiros valores depois do Passa-Baixa
# print("Passa-Baixa:", teste_passa_baixa[:5])

# # mostra os 5 primeiros valores depois do Passa-Alta
# print("Passa-Alta:", teste_passa_alta[:5])

# # mostra os 5 primeiros valores depois do Passa-Banda
# print("Passa-Banda:", teste_passa_banda[:5])

# # mostra os 5 primeiros valores depois do Notch
# print("Notch:", teste_notch[:5])

# # mostra os 5 primeiros valores do pipeline completo (sinal limpo final)
# print("Sinal Limpo:", sinal_limpo[:5])

# # =====================================================================
# # VISUALIZAÇÃO GRÁFICA COM MATPLOTLIB
# # =====================================================================

# # cria uma figura com 2 gráficos empilhados (2 linhas, 1 coluna), compartilhando o eixo X
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)

# # desenha o sinal ORIGINAL (bruto) no primeiro gráfico, em vermelho
# ax1.plot(canal_original, color='crimson', alpha=0.8, label='Sinal Bruto (Canal O1)')

# # define o título do primeiro gráfico
# ax1.set_title('EEG Bruto - Sem Tratamento (Com Offset DC e Ruído Elétrico)')

# # define o nome do eixo Y do primeiro gráfico
# ax1.set_ylabel(r'Amplitude ($\mu V$)')

# # mostra a legenda (nome da linha) no canto superior direito
# ax1.legend(loc='upper right')

# # ativa as linhas de grade no primeiro gráfico
# ax1.grid(True)

# # desenha o sinal LIMPO (já filtrado) no segundo gráfico, em azul-esverdeado
# ax2.plot(sinal_limpo, color='teal', label='Sinal Filtrado (Detrend + Notch 60Hz + Bandpass 8-13Hz)')

# # define o título do segundo gráfico
# ax2.set_title('EEG Processado - Sinal Limpo (Faixa Alfa)')

# # define o nome do eixo X do segundo gráfico
# ax2.set_xlabel('Número de Amostras')

# # define o nome do eixo Y do segundo gráfico
# ax2.set_ylabel(r'Amplitude ($\mu V$)')

# # mostra a legenda do segundo gráfico
# ax2.legend(loc='upper right')

# # ativa as linhas de grade no segundo gráfico
# ax2.grid(True)

# # ajusta os espaçamentos entre os elementos, pra não ficar apertado
# plt.tight_layout()

# # exibe a janela com os dois gráficos na tela
# plt.show()

# # define qual board estamos simulando/seguindo (Synthetic, nesse caso)
# board_id = BoardIds.SYNTHETIC_BOARD.value  # ou o board correto usado na gravação

# # pergunta pro BrainFlow quais posições do array são canais de EEG (nesse caso, do Synthetic)
# eeg_channels = BoardShim.get_eeg_channels(board_id)

# # pega todas as linhas (canais), mas só as primeiras 1000 colunas (um pedaço menor)
# dados_reduzidos = dados[:, :1000].copy()

# # mostra na tela o novo tamanho reduzido do array
# print("Dimensões reduzidas:", dados_reduzidos.shape)

# # percorre cada linha do array completo, mostrando a posição e os 3 primeiros valores
# for indice, linha in enumerate(dados):
#     # imprime o número da linha e uma prévia dos valores, só pra inspecionar visualmente
#     print("Linha", indice, ":", linha[:3])

# # filtra SÓ os canais de EEG, preservando as outras linhas (timestamp, etc)
# # CORRIGIDO: 19.0, 22.0 (centro/largura, versão do Pedro) → 8, 13 (start/stop, faixa Alfa)
# for canal in eeg_channels:
#     DataFilter.detrend(dados_reduzidos[canal], DetrendOperations.CONSTANT.value)
#     DataFilter.perform_bandstop(dados_reduzidos[canal], frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)
#     DataFilter.perform_bandpass(dados_reduzidos[canal], frequencia_amostragem, 8, 13, 4, FilterTypes.BUTTERWORTH.value, 0)

# # salva essa versão reduzida e já filtrada num arquivo novo, menor que o anterior
# DataFilter.write_file(dados_reduzidos, 'gravacao_olhos_fechados_pequena.csv', 'w')

# # avisa na tela que deu tudo certo
# print("Arquivo filtrado reduzido salvo com sucesso!")



# Vai até a biblioteca BrainFlow e pega duas ferramentas
# DataFilter - onde ficam as funções de ler arquivo e filtrar
# FilterTypes - uma lista de tipos de filtro matemático que podemos escolher
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

# traz BoardShim e BoardIds, usados pra identificar informações sobre o board
from brainflow.board_shim import BoardShim, BoardIds

# Ferramenta de gráficos visuais do Python
import matplotlib.pyplot as plt

# Abre o arquivo gravacao_olhos_aberto.csv e guarda todo o conteúdo dele
# (array completo: cada linha é um canal diferente)
dados = DataFilter.read_file('gravacao_olhos_abertos_teste3.csv') # gravacao_ruido.csv gravacao_olhos_fechados.csv gravacao_olhos_abertos.csv

# mostra na tela o TIPO da variável "dados" (confirma que é um array numpy)
print("Tipo dos dados:", type(dados))

# mostra na tela as DIMENSÕES do array (quantas linhas, quantas colunas)
print("Dimensões dos dados:", dados.shape)

# guarda a taxa de amostragem real (160Hz) numa variável, pra reutilizar depois
frequencia_amostragem = 160

# pega a linha correspondente ao canal O1 (posição 7), e faz uma cópia
# essa cópia vai ficar intacta, representando o sinal "bruto" original
canal_original = dados[7].copy()

# cria outra cópia, que vai ser usada pra fazer o processamento/filtros
canal_processamento = canal_original.copy()

# remove o offset DC (um desvio constante) somente da cópia de processamento
DataFilter.detrend(canal_processamento, DetrendOperations.CONSTANT.value)

# TESTE 1: FILTRO PASSA-BAIXA
# cria uma cópia independente, partindo do sinal já sem offset DC
teste_passa_baixa = canal_processamento.copy()

# aplica o filtro Passa-Baixa: deixa passar só frequência baixa, corta acima de 30Hz
# parâmetros: (sinal, taxa de amostragem, frequência de corte, ordem, tipo matemático, ripple)
DataFilter.perform_lowpass(teste_passa_baixa, frequencia_amostragem, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 2: FILTRO PASSA-ALTA
# cria outra cópia nova, partindo do processamento (não da cópia anterior)
teste_passa_alta = canal_processamento.copy()

# aplica o filtro Passa-Alta: deixa passar só frequência alta, corta abaixo de 8Hz
DataFilter.perform_highpass(teste_passa_alta, frequencia_amostragem, 8, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 3: FILTRO PASSA-BANDA
# mais uma cópia nova, também a partir do processamento
teste_passa_banda = canal_processamento.copy()

# aplica o filtro Passa-Banda: deixa passar só 8-13Hz (faixa da Alfa)
# parâmetros: (sinal, taxa de amostragem, início da faixa, fim da faixa, ordem, tipo, ripple)
DataFilter.perform_bandpass(teste_passa_banda, frequencia_amostragem, 8, 13, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 4: FILTRO NOTCH
# última cópia nova, também partindo do processamento
teste_notch = canal_processamento.copy()

# aplica o filtro Notch: remove só a faixa de 58-62Hz (interferência elétrica)
# parâmetros: (sinal, taxa de amostragem, início da faixa a remover, fim da faixa, ordem, tipo, ripple)
DataFilter.perform_bandstop(teste_notch, frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# TESTE 5: PIPELINE COMPLETO (Sinal Limpo Final)
# cria uma cópia que vai receber TODOS os filtros em sequência
sinal_limpo = canal_processamento.copy()

# remove o ruído de 60Hz da rede elétrica
DataFilter.perform_bandstop(sinal_limpo, frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)

# isola a faixa da Alfa (8 a 13Hz)
DataFilter.perform_bandpass(sinal_limpo, frequencia_amostragem, 8, 13, 4, FilterTypes.BUTTERWORTH.value, 0)

# mostra os 5 primeiros valores do sinal original, sem filtro nenhum
print("Original:", canal_original[:5])

# mostra os 5 primeiros valores depois do Passa-Baixa
print("Passa-Baixa:", teste_passa_baixa[:5])

# mostra os 5 primeiros valores depois do Passa-Alta
print("Passa-Alta:", teste_passa_alta[:5])

# mostra os 5 primeiros valores depois do Passa-Banda
print("Passa-Banda:", teste_passa_banda[:5])

# mostra os 5 primeiros valores depois do Notch
print("Notch:", teste_notch[:5])

# mostra os 5 primeiros valores do pipeline completo (sinal limpo final)
print("Sinal Limpo:", sinal_limpo[:5])

# =====================================================================
# VISUALIZAÇÃO GRÁFICA COM MATPLOTLIB
# =====================================================================

# cria uma figura com 2 gráficos empilhados (2 linhas, 1 coluna), compartilhando o eixo X
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)

# desenha o sinal ORIGINAL (bruto) no primeiro gráfico, em vermelho
ax1.plot(canal_original, color='crimson', alpha=0.8, label='Sinal Bruto (Canal O1)')

# define o título do primeiro gráfico
ax1.set_title('EEG Bruto - Sem Tratamento (Com Offset DC e Ruído Elétrico)')

# define o nome do eixo Y do primeiro gráfico
ax1.set_ylabel(r'Amplitude ($\mu V$)')

# mostra a legenda (nome da linha) no canto superior direito
ax1.legend(loc='upper right')

# ativa as linhas de grade no primeiro gráfico
ax1.grid(True)

# desenha o sinal LIMPO (já filtrado) no segundo gráfico, em azul-esverdeado
ax2.plot(sinal_limpo, color='teal', label='Sinal Filtrado (Detrend + Notch 60Hz + Bandpass 8-13Hz)')

# define o título do segundo gráfico
ax2.set_title('EEG Processado - Sinal Limpo (Faixa Alfa)')

# define o nome do eixo X do segundo gráfico
ax2.set_xlabel('Número de Amostras')

# define o nome do eixo Y do segundo gráfico
ax2.set_ylabel(r'Amplitude ($\mu V$)')

# mostra a legenda do segundo gráfico
ax2.legend(loc='upper right')

# ativa as linhas de grade no segundo gráfico
ax2.grid(True)

# ajusta os espaçamentos entre os elementos, pra não ficar apertado
plt.tight_layout()

# exibe a janela com os dois gráficos na tela
plt.show()

# # define qual board estamos simulando/seguindo (Synthetic, nesse caso)
# board_id = BoardIds.SYNTHETIC_BOARD.value  # ou o board correto usado na gravação

# # pergunta pro BrainFlow quais posições do array são canais de EEG (nesse caso, do Synthetic)
# eeg_channels = BoardShim.get_eeg_channels(board_id)

# em vez de perguntar pro BrainFlow (que não conhece esse CSV manual),
# usamos diretamente as posições que SABEMOS que são os 16 canais reais
# (de acordo com o jeito que o converter_edf.py montou o arquivo)
eeg_channels = range(1, 17)

# percorre cada linha do array completo, mostrando a posição e os 3 primeiros valores
for indice, linha in enumerate(dados):
    # imprime o número da linha e uma prévia dos valores, só pra inspecionar visualmente
    print("Linha", indice, ":", linha[:3])

# aplica o filtro em TODOS os canais de EEG, usando o array COMPLETO
# (antes usava "dados_reduzidos", limitado a 1000 amostras — agora usa "dados" 
# inteiro, respeitando o tamanho real do arquivo, seja ele de 1 minuto ou outro)
for canal in eeg_channels:
    # remove o offset DC de cada canal
    DataFilter.detrend(dados[canal], DetrendOperations.CONSTANT.value)
    # remove a interferência elétrica (60Hz) de cada canal
    DataFilter.perform_bandstop(dados[canal], frequencia_amostragem, 58, 62, 4, FilterTypes.BUTTERWORTH.value, 0)
    # isola a faixa da Alfa (8-13Hz) em cada canal
    DataFilter.perform_bandpass(dados[canal], frequencia_amostragem, 8, 13, 4, FilterTypes.BUTTERWORTH.value, 0)

# salva o arquivo COMPLETO já filtrado, com nome mais descritivo
DataFilter.write_file(dados, 'gravacao_olhos_abertos_filtrada_teste3.csv', 'w')

# avisa na tela que deu tudo certo, já identificando qual arquivo foi gerado
print("Arquivo filtrado (tamanho completo) salvo com sucesso em gravacao_olhos_fechados_filtrada.csv!")