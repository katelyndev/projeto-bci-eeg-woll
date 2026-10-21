# traz as 3 ferramentas do BrainFlow: gerenciador de conexão, caixa de configurações, e lista de fontes possíveis
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
# traz a ferramenta de tempo, pra poder pausar o código e pegar o horário atual
import time
# traz a ferramenta que transforma um horário "cru" em texto legível (data/hora formatada)
from datetime import datetime

# cria a caixa de configurações vazia (o modo simulado não precisa de detalhe nenhum)
params = BrainFlowInputParams()
# escolhe a fonte de dados: o simulador (Synthetic Board)
board_id = BoardIds.SYNTHETIC_BOARD.value
# monta o gerenciador de conexão, juntando a fonte escolhida com as configurações
board = BoardShim(board_id, params)

# prepara a conexão internamente, arrumando tudo antes de começar
board.prepare_session()
# liga de fato o fluxo de dados simulados
board.start_stream()
# pausa o código por 10 segundos, dando tempo do simulador gerar dados
time.sleep(10)
# pega todos os dados gerados nesses 10 segundos, guardando na variável "dados"
dados = board.get_board_data()
# desliga o fluxo de dados
board.stop_stream()
# libera os recursos reservados na conexão
board.release_session()

# cria uma lista com as 4 linhas de cabeçalho que o formato do Playback exige
cabecalho = [
    "%OpenBCI Raw EXG Data",
    "%Number of channels = 16",
    "%Sample Rate = 125 Hz",
    "%Board = Cyton+Daisy"
]
# monta a lista com os nomes de todas as 33 colunas, juntando várias listas menores com "+"
colunas = (
    ["Sample Index"] +  # nome da primeira coluna: índice da amostra
    [f"EXG Channel {i}" for i in range(16)] +  # gera automaticamente "EXG Channel 0" até "EXG Channel 15"
    ["Accel Channel 0", "Accel Channel 1", "Accel Channel 2"] +  # colunas do acelerômetro (x, y, z)
    ["Not Used"] +  # coluna reservada, sem uso
    ["Digital Channel 0 (D11)", "Digital Channel 1 (D12)", "Digital Channel 2 (D13)", "Digital Channel 3 (D17)"] +  # canais digitais
    ["Not Used"] +  # outra coluna reservada, sem uso
    ["Digital Channel 4 (D18)"] +  # mais um canal digital
    ["Analog Channel 0", "Analog Channel 1", "Analog Channel 2"] +  # canais analógicos
    ["Timestamp", "Marker Channel", "Timestamp (Formatted)"]  # carimbo de tempo, marcador, e hora legível
)

# abre (cria) o arquivo "gravacao_playback.csv" para escrita ("w"), fechando sozinho no final
with open("gravacao_playback.csv", "w") as f:
    # escreve cada uma das 4 linhas do cabeçalho, uma embaixo da outra
    for linha in cabecalho:
        f.write(linha + "\n")
    # escreve os nomes das colunas numa única linha, separados por vírgula
    f.write(", ".join(colunas) + "\n")

    # descobre quantas amostras (colunas de dados) existem no total
    num_amostras = dados.shape[1]
    # repete esse bloco uma vez para cada amostra
    for i in range(num_amostras):
        # pega o horário atual (número cru, tipo timestamp Unix)
        agora = time.time()
        # transforma esse horário num texto legível, cortando os 3 últimos dígitos dos microssegundos
        agora_formatado = datetime.fromtimestamp(agora).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # calcula o índice da amostra, reiniciando de 0 a 255 em ciclos
        sample_index = i % 256
        # pega os 16 canais EEG (linhas 1 a 16) só dessa amostra específica (coluna i)
        exg = dados[1:17, i].tolist()
        # preenche com zero, já que não temos dado real de acelerômetro
        accel = [0.0, 0.0, 0.0]
        # preenche a coluna reservada com zero
        not_used_1 = [0.0]
        # preenche os canais digitais com zero
        digital_1 = [0.0, 0.0, 0.0, 0.0]
        # preenche a segunda coluna reservada com zero
        not_used_2 = [0.0]
        # preenche o quinto canal digital com zero
        digital_2 = [0.0]
        # preenche os canais analógicos com zero
        analog = [0.0, 0.0, 0.0]
        # preenche o marcador com zero (nenhum evento marcado)
        marker = [0.0]

        # junta tudo numa única lista, na ordem exata que o formato exige
        linha_completa = (
            [sample_index] + exg + accel + not_used_1 +
            digital_1 + not_used_2 + digital_2 + analog +
            [agora, marker[0], agora_formatado]
        )
        # transforma cada valor da lista em texto, junta tudo separado por vírgula, e escreve a linha no arquivo
        f.write(", ".join(map(str, linha_completa)) + "\n")

# avisa que o processo terminou, confirmando o nome do arquivo gerado
print("Gravação completa (33 colunas), salva em gravacao_playback.csv")