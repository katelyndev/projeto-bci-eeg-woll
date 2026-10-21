# vai ate a biblioteca BrainFlow e pega 3 ferramentas dela 
# BoardShim = peca principal que gerencia toda a conexao com a fonte de dados 
# BrainFlowInputParams = é o molde de criar uma caixa de configuração de conexão 
# BoardIds = é a lista de qual fonte quer usar (Synthetic, Cyton, Playback)
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# Traz a biblioteca de graficos | aqui demos um apelido para a biblioteca entao é so chamar com plt.algo()
import matplotlib.pyplot as plt

import time

#aqui é a criação da caixa de configuracao vazia, usando o molde da primira linha 
configConex = BrainFlowInputParams()

# BoardsIds lista de opcoes prontas dentro do BrainFlow, onde cada fonte de tipo de dados tem um numero de indentificacao proprio para saber qual tipo de conexao vc quer | modo simulado
fonte = BoardIds.SYNTHETIC_BOARD.value # aqui troca qual fonte usar 

# esse é o gerenciador de conexoes | qual tipo de conexao | config extras e guardadno em board 
board = BoardShim(fonte, configConex)
# aqui tem a preparacao para fazer a conexao 
board.prepare_session()
# aqui recebe e gera dados de verdade 
board.start_stream()
# pega tudo que ja foi gerado/capturado e uarda esse pacote de dados em uma variavel dados | sendo organizado em um formato de tabela 
dados = board.get_board_data()

# é a parte interativa do grafico | ografico se atualiza sozinho
plt.ion()
#cria a estrutura do grafico 
# fig = figura - a janela interia que aparece na tela 
# ax = eixos - é a area de dentro | onde a linha do sinale é desenhada 
fig, ax = plt.subplots()

try:
    for i in range(30):  # roda por mais tempo agora (30 ciclos)
        time.sleep(1)
        dados = board.get_board_data()
        if dados.shape[1] > 0:
            canal_1 = dados[0]  # pega só o primeiro canal, pra não poluir o gráfico
            ax.clear()
            ax.plot(canal_1)
            ax.set_title(f"Canal 1 - ciclo {i+1}")
            plt.pause(0.01)
finally:
    
    # para a geração continua de dados  
    board.stop_stream()
    # libera todos os recurso que tinham sido reservados na hora de preparar 
    board.release_session()
    print("Sessão encerrada.")