#traz para o python a ferramenta de rede | modulo pronto que permite sendo a ponte para que o python usar essa api sem escrever linguagem de baixo nivel
import socket

# ferramenta que sabe entender textos no formato JSON e transformar em algo que o Python consegue manipular de verdade 
import json

# biblioteca principal do matplotlib | configurar algo antes de usar a parte de desenho 
import matplotlib
# aqui escolhendo manualmente qual o motor de desenho para mostrar o grafico
matplotlib.use('TkAgg')

# Traz a biblioteca de graficos | aqui demos um apelido para a biblioteca entao é so chamar com plt.algo()
import matplotlib.pyplot as plt

# guarda o endereco e a porta onde via escutar os sinais
UDP_IP = "127.0.0.1" #o proprio computador/localmente
UDP_PORT = 12345 #numero da portinha igual ao que esta configurado no app | qual prograa deve receber qual dado

# objeto de comunicação | AF_INET = tipo IPv4(formato mais comun da internet) | SOCK_DGRAM = tipo UDP (sem confirmação de entrega, mais rápido) 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# reservar aquele endereço+porta só pro seu programa escutar ali | metodo 
sock.bind((UDP_IP, UDP_PORT))
#sock do proprio python serve para comunicacao em rede 

# é a parte interativa do grafico | ografico se atualiza sozinho
plt.ion()
#cria a estrutura do grafico 
# fig = figura - a janela interia que aparece na tela 
# ax = eixos - é a area de dentro | onde a linha do sinale é desenhada 
fig, ax = plt.subplots()

# mensagem visual que o programa rodou ate aqui 
print(f"Esperando dados do OpenBCI GUI em {UDP_IP}:{UDP_PORT}...")

# um laco de repeticao sem fim, o intuito é ficar rodando sem fim escutando o sinal, so para quando eu mandar parar
while True:
    data, addr = sock.recvfrom(4096) #realmente pausa e espera até algo chegar na porta | data = valores em si | addr = de onde veio | 4096 = tamanho maximo em byts que vai receber de uma vez
    try: #abre o bloco de tentaiva tudo que esta dentro o python tentara executar, em vez de travar o programa se der erro ele pula direto para except 

        pacote = json.loads (data.decode("utf-8")) #json.loads = pega esse json e trnsforma em uma estrutura de python |data chega como bytes que não é texto normal pro Python entender direto. .decode("utf-8") converte esses bytes pra uma string legível

        canais = pacote["data"] # vai do canal um a 16 | ele da o valor que esta guardado em data sem precisar ir manualemnte

        #pega o numero so do primeiro canal | so para facilitar usar na proxima linha 
        canal_1 = canais[0]
        # apaga o desenho anterior da area de grafico | so linha mais recente 
        ax.clear()
        # desenha a nova linha usando os numeros que acabaram de chegar 
        ax.plot(canal_1)
        # da uma pausa curtinha para para a tela realmente atualizar e mostrtar o grafico 
        plt.pause(0.01)

        # pacote['type'] = mostra o tipo do dado  | len(canais) = len conta quantos itens tem dentro de algo (16) | len(canais[0]) → canais[0] pega a primeira lista (o canal 1); len(...) conta quantos números tem dentro dela 
        print(f"Tipo: {pacote['type']} | Canais recebidos: {len(canais)} | Amostras por canal: {len(canais[0])}")

    # caso algo dentro do try falhe. Ele só entra em ação se acontecer um desses 3 tipos de erro:
    #json.JSONDecodeError = o texto recebido não era um JSON válido (veio quebrado/incompleto)
    #KeyError = tentou acessar uma chave que não existe (ex: não tinha "data" naquele pacote)
    #IndexError = tentou pegar canais[0], mas a lista estava vazia
    #as erro = guarda os detalhes desse erro numa variável, pra você poder ver o que aconteceu.
    except (json.JSONDecodeError, KeyError, IndexError) as erro:
        print("Pacote ignorado (formato inesperado):", erro) #em vez de travar tudo o pacote so fala que deu um erro
    # print("Dado recebido:", data.decode("utf-8")) #data chega como bytes que não é texto normal pro Python entender direto. .decode("utf-8") converte esses bytes pra uma string legível