# Importa as ferramentas do Flask
from flask import Flask, jsonify, send_file

# Cria nossa aplicação web
app = Flask(__name__)

# Define a rota raiz ("/") e associa à função abrir_pagina
@app.route("/")
def abrir_pagina():
    return send_file("index.html")

# Associa a rota /estado à função abaixo
@app.route("/estado")

# Define a função que será executada
def obter_estado():

    # Devolve o estado em formato JSON
    return jsonify({"estado": 0})

# Inicia o servidor para testes locais
app.run(debug=True)