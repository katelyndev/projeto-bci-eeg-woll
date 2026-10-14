# traz as 3 ferramentas do BrainFlow: gerenciador de conexão, caixa de configurações, e lista de fontes possíveis
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# traz a ferramenta de tempo, pra poder pausar o código e pegar o horário atual
import time

# traz a ferramenta que formata hora legível
from datetime import datetime

# cria a caixa de configurações vazia (o modo simulado não precisa de detalhe nenhum)
params = BrainFlowInputParams()

# a caixa de ferramentas esta sendo preenchida com um caminho da gravacao | queremos que BrainFlow leia dados prontos nao gere do zero
# params.file = "/home/woll-ai/Projetos/BCI/gravacao_16canais.csv"
# params.file = "/home/woll-ai/Projetos/BCI/gravacao_ruido.csv"
# params.file = "/home/woll-ai/Projetos/BCI/gravacao_filtrada.csv"
# params.file = "/home/woll-ai/Projetos/BCI/gravacao_olhos_fechados.csv"
# params.file = "/home/woll-ai/Projetos/BCI/gravacao_olhos_abertos.csv"
# params.file = "/home/woll-ai/projeto-bci-eeg-woll/gravacao_olhos_fechados.csv"
params.file = "/home/woll-ai/Projetos/BCI/gravacao_olhos_fechados_filtrada.csv"
# params.file = "/home/woll-ai/Projetos/BCI/gravacao_olhos_abertos_filtrada.csv"

# preenche outro campo da caixa de ferramentas mostrando que esse arquivo é do tipo board synthetic (qual estrutura esperar)
params.master_board = BoardIds.SYNTHETIC_BOARD.value

# pergunta pro BrainFlow qual é a taxa de amostragem usada pelo Synthetic Board
taxa_synthetic = BoardShim.get_sampling_rate(params.master_board)

# mostra essa taxa na tela, só pra conferir
print("Taxa do Synthetic Board:", taxa_synthetic, "Hz")

# # se os dados tivessem vindo da placa real Cyton+Daisy
# params.master_board = BoardIds.CYTON_DAISY_BOARD

# BoardIds = o catálogo de todas as opções possíveis de fonte de dados
# .PLAYBACK_FILE_BOARD = a opção específica dentro desse catálogo, que representa "ler de um arquivo"
# .value = pega o número que representa essa opção (o BrainFlow trabalha com números internamente, não com o nome por extenso)
# board_id = ... = guarda esse número numa variável, pra usar logo em seguida
board_id = BoardIds.PLAYBACK_FILE_BOARD.value

# junta qual mecanismo usar + as configuracoes detalhadas em um unico gerenciador de conexao
board = BoardShim(board_id, params)

# prepara a conexão internamente, arrumando tudo antes de começar
board.prepare_session()

print("Início do envio:", datetime.now().strftime("%H:%M:%S"))

# liga a transmissao de dados ele nao so gera e guarda na memoria ele envia pela rede | o brainFlow comeca a ler o arquivo
board.start_stream(45000, 'streaming_board://225.1.1.1:6677')

# pausa o código por 60 segundos, dando tempo do simulador gerar dados | quanto maior o tempo maior a quantidade do arquivo sera transmitido
time.sleep(60)

print("Fim da espera (60s):", datetime.now().strftime("%H:%M:%S"))

# para a geração continua de dados
board.stop_stream()
# libera todos os recurso que tinham sido reservados na hora de preparar
board.release_session()
print("Transmissão encerrada.")