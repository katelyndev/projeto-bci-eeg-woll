# vai ate a biblioteca BrainFlow e pega 3 ferramentas dela 
# BoardShim = peca principal que gerencia toda a conexao com a fonte de dados 
# BrainFlowInputParams = é o molde de criar uma caixa de configuração de conexão 
# BoardIds = é a lista de qual fonte quer usar (Synthetic, Cyton, Playback)
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import time # traz a ferramenta que espera um tempo necesario 

# Prepara os parâmetros de conexão (vazios porque o Synthetic Board não precisa de porta/cabo)
params = BrainFlowInputParams()

# Escolhe o board sintético (gera dados falsos, sem hardware)
board_id = BoardIds.SYNTHETIC_BOARD.value

# monta o gerenciador de conexão de verdade, juntando a fonte escolhida com as configurações 
board = BoardShim(board_id, params)

# so avisa pelo terminal
print("Preparando sessão com o Synthetic Board...")
# prepara a conexao antes de gerar dados 
board.prepare_session()

print("Iniciando o stream de dados...")
# liga a geracao continua de dados simulados 
board.start_stream()

print("Coletando dados por 5 segundos...")
# isso da tempo do simulador encher de dados 
time.sleep(5)

# Pega os dados coletados até agora
data = board.get_board_data()

print(f"\nFormato dos dados (canais x amostras): {data.shape}")
print(f"Primeiras 5 amostras do canal 1:\n{data[1][:5]}")

# para a geração continua de dados  
board.stop_stream()
# libera todos os recurso que tinham sido reservados na hora de preparar 
board.release_session()

print("\nSessão finalizada com sucesso!")
