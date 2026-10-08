# Vai até a biblioteca BrainFlow e pega duas ferramentas
# DataFilter - onde ficam as funções de ler arquivo e filtrar
# FilterTypes - uma lista de tipos de filtro matemático que podemos escolher
from brainflow.data_filter import DataFilter, FilterTypes

# Abre o arquivo gravacao_ruido.csv e guarda todo o conteúdo dele
# (array completo: cada linha é um canal diferente)
dados = DataFilter.read_file('gravacao_ruido.csv')

# pega só uma linha desse array inteiro
# esse será o sinal "puro", que vamos preservar sem mexer
canal_original = dados[3]

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

# mostra os 5 primeiros valores de cada versão, só pra conferir rapidamente
print("Original:", canal_original[:5])
print("Passa-Baixa:", teste_passa_baixa[:5])
print("Passa-Alta:", teste_passa_alta[:5])
print("Passa-Banda:", teste_passa_banda[:5])
print("Notch:", teste_notch[:5])

from brainflow.board_shim import BoardShim, BoardIds

board_id = BoardIds.SYNTHETIC_BOARD.value  # ou o board correto usado na gravação
eeg_channels = BoardShim.get_eeg_channels(board_id)

# pega todas as linhas (todos os canais), mas só as primeiras 1000 colunas
# isso corta o sinal em um pedaço menor (cerca de 8 segundos, já que fs=125)
# o objetivo é reduzir o tamanho do arquivo final, pra testar se isso resolve
# a instabilidade do Streaming Board com arquivos grandes
dados_reduzidos = dados[:, :1000].copy()

# repete o filtro Passa-Banda, só que agora na versão reduzida do sinal
# continua filtrando só os canais de EEG de verdade (eeg_channels),
# igual fizemos antes, pra não estragar as linhas de contagem/metadado
for canal in eeg_channels:
    DataFilter.perform_bandpass(dados_reduzidos[canal], 125, 8, 30, 4, FilterTypes.BUTTERWORTH.value, 0)

# salva essa versão reduzida e já filtrada num arquivo novo, menor que o anterior
DataFilter.write_file(dados_reduzidos, 'gravacao_filtrada_pequena.csv', 'w')

# avisa na tela que deu tudo certo
print("Arquivo filtrado reduzido salvo com sucesso!")