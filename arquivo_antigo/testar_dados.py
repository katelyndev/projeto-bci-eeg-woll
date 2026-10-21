# traz as ferramentas do BrainFlow, as mesmas que você já usa
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter
import time

# cria a caixa de configurações, igual você já faz
params = BrainFlowInputParams()

# diz que não vamos ler de ARQUIVO, vamos RECEBER da rede (streaming)
params.ip_address = "225.1.1.1"
params.ip_port = 6677

# usa o board "Streaming Board", que é o "modo consumidor" (quem recebe)
board_id = BoardIds.STREAMING_BOARD.value

# monta o gerenciador de conexão, em modo "ouvinte"
board = BoardShim(board_id, params)

# prepara a sessão (como consumidor, não como quem envia)
board.prepare_session()

# começa a "escutar" o que está chegando pela rede
board.start_stream()

# espera uns 15 segundos, tempo suficiente pra receber bastante dado
time.sleep(15)

# para de escutar
board.stop_stream()

# pega TUDO que foi recebido durante esse tempo
dados_recebidos = board.get_board_data()

# libera a sessão
board.release_session()

# salva o que foi RECEBIDO pela rede, num arquivo novo pra comparar
DataFilter.write_file(dados_recebidos, 'teste_recebido_pela_rede.csv', 'w')

print("Dados recebidos salvos em teste_recebido_pela_rede.csv!")