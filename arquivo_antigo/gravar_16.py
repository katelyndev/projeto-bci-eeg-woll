# traz as 3 ferramentas do BrainFlow: gerenciador de conexão, caixa de configurações, e lista de fontes possíveis
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
# traz a ferramenta de tempo, pra poder pausar o código
import time

# cria a caixa de configurações vazia (o modo simulado não precisa de detalhe nenhum)
params = BrainFlowInputParams()
# escolhe a fonte de dados: o simulador (Synthetic Board)
board_id = BoardIds.SYNTHETIC_BOARD.value
# monta o gerenciador de conexão, juntando a fonte escolhida com as configurações
board = BoardShim(board_id, params)

# prepara a conexão internamente, arrumando tudo antes de começar
board.prepare_session()
# liga o fluxo de dados E, ao mesmo tempo, grava direto num arquivo (usando o streamer nativo do BrainFlow)
board.start_stream(45000, 'file://gravacao_16canais.csv:w')
# pausa o código por 10 segundos, dando tempo do simulador gerar e gravar dados
time.sleep(30)
# desliga o fluxo de dados (e, junto, finaliza a escrita no arquivo)
board.stop_stream()
# libera os recursos reservados na conexão
board.release_session()

# avisa que o processo terminou, confirmando o nome do arquivo gerado
print("Gravação salva em gravacao_16canais.csv")