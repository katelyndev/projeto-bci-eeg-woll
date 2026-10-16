# Importa as ferramentas do Flask
from flask import Flask, jsonify, send_file

# traz a função que o front vai usar pra receber os resultados da simulação
from decisao_olhos import iniciar_simulacao

# traz a ferramenta de threading, pra rodar a simulação numa "linha paralela" | roda mais tarefas ao mesmo tempo
import threading

# Cria nossa aplicação web
app = Flask(__name__)

#guarda o estado atual
estado_atual = 0

# função que atualiza a variável "estado_atual", toda vez que a simulação calcular um novo valor
def atualizar_estado(novo_estado):
    # avisa que vamos mexer na variável "estado_atual" que foi criada lá fora, não numa nova
    global estado_atual
    estado_atual = novo_estado

# função que roda a simulação inteira, numa linha separada do servidor
def rodar_simulacao():
    iniciar_simulacao(atualizar_estado, delay=3)

# cria a "linha paralela" (thread), ligada à função rodar_simulacao
thread = threading.Thread(target=rodar_simulacao, daemon=True)
# inicia essa linha paralela, ANTES do servidor começar a escutar pedidos
thread.start()

# Define a rota raiz ("/") e associa à função abrir_pagina
@app.route("/")
def abrir_pagina():
    return send_file("index.html")

# Associa a rota /estado à função abaixo
@app.route("/estado")

# Define a função que será executada
def obter_estado():

    # Devolve o estado em formato JSON
    return jsonify({"estado": estado_atual})

# Inicia o servidor para testes locais
app.run(debug=True)