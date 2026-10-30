import argparse
import threading
import time
from pathlib import Path

from flask import Flask, jsonify
from decisao_beta_ica import preparar_comparacao as comparar_pessoa1
from decisao_beta_ica_pessoa3 import preparar_comparacao as comparar_pessoa3


# Escolhe qual gravação será usada na demonstração.
parser = argparse.ArgumentParser()
parser.add_argument(
    "--versao",
    choices=("antes_ica", "depois_ica"),
    default="antes_ica"
)

parser.add_argument(
    "--pessoa",
    type=int,
    choices=(1, 3),
    default=1
)
args = parser.parse_args()

if args.pessoa == 1:
    referencia, resultados = comparar_pessoa1()
else:
    referencia, resultados = comparar_pessoa3()

# Localiza a interface da Katelyn.
PASTA_INTERFACE = (
    Path(__file__).resolve().parent.parent
    / "experimento_concentracao"
)

app = Flask(
    __name__,
    static_folder=str(PASTA_INTERFACE / "static"),
    static_url_path="/static"
)

estado_atual = 0
iniciada = False
trava = threading.Lock()


def rodar_simulacao():
    global estado_atual

    # Espera a página aparecer antes da primeira decisão.
    time.sleep(2)

    print(f"\nVersão: {args.versao}")
    print(f"Referência compartilhada: {referencia:.4f} µV²")

    estados = resultados[args.versao]

    for condicao in ("repouso", "foco"):
        esperado = 0 if condicao == "repouso" else 1

        for numero, estado in enumerate(
            estados[condicao], start=1
        ):
            with trava:
                estado_atual = int(estado)

            print(
                f"{condicao} | janela {numero} | "
                f"previsto: {estado} | esperado: {esperado}"
            )

            time.sleep(3)

    print("\nDemonstração encerrada.")
    print("O quadrado mantém a última previsão.")


@app.route("/")
def abrir_pagina():
    global iniciada

    pagina = (
        PASTA_INTERFACE / "index.html"
    ).read_text(encoding="utf-8")

    # Acrescenta a identificação do experimento.
    pagina = pagina.replace(
        "</h1>",
        "</h1>"
        f"<p>Pessoa {args.pessoa} — versão: "
        f"<strong>{args.versao}</strong></p>"
        "<p>Azul: previsão de foco (1). "
        "Vermelho: previsão de repouso (0).</p>"
        "<p>Teste experimental: a previsão não confirma "
        "o estado de concentração.</p>",
        1
    )

    # Oculta o botão que alterava a cor manualmente.
    pagina = pagina.replace(
        "</head>",
        "<style>#botao { display: none; }</style></head>",
        1
    )

    # Identifica os resultados como previsões.
    pagina = pagina.replace(
        'mensagem.textContent = "Concentrado";',
        'mensagem.textContent = "Previsão: foco";'
    )
    pagina = pagina.replace(
        'mensagem.textContent = "Não concentrado";',
        'mensagem.textContent = "Previsão: repouso";'
    )

    # Declara explicitamente o elemento usado pelo JavaScript.
    pagina = pagina.replace(
        "const quadrado = document.getElementById('quadrado');",
        "const quadrado = document.getElementById('quadrado');\n"
        "const mensagem = document.getElementById('mensagem');",
        1
    )

    # Inicia uma única sequência ao abrir a página.
    with trava:
        if not iniciada:
            iniciada = True
            threading.Thread(
                target=rodar_simulacao,
                daemon=True
            ).start()

    return pagina


@app.route("/estado")
def obter_estado():
    with trava:
        estado = estado_atual

    return jsonify({"estado": estado})


if __name__ == "__main__":
    app.run(
        port=5001,
        debug=False,
        use_reloader=False
    )