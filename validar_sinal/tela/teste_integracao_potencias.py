
from validar_sinal.tela.ler_potencias import ler_potencias

# Simula duas janelas, com os dois canais necessários
potencias_teste = [
    [
        {
            "canal": "EEG Fpz-Cz",
            "delta": 45.2,
            "theta": 18.7,
            "alfa": 11.3,
            "beta": 6.9,
            "unidade": "uV²"
        },
        {
            "canal": "EEG Pz-Oz",
            "delta": 40.1,
            "theta": 16.5,
            "alfa": 10.8,
            "beta": 6.2,
            "unidade": "uV²"
        }
    ],
    [
        {
            "canal": "EEG Fpz-Cz",
            "delta": 42.0,
            "theta": 17.0,
            "alfa": 12.0,
            "beta": 7.0,
            "unidade": "uV²"
        },
        {
            "canal": "EEG Pz-Oz",
            "delta": 39.0,
            "theta": 15.0,
            "alfa": 10.0,
            "beta": 6.0,
            "unidade": "uV²"
        }
    ]
]

# Confere a estrutura que o leitor recebe
print("Quantidade de janelas:", len(potencias_teste))

for numero, janela in enumerate(potencias_teste, start=1):
    print(f"\nJanela {numero}:")
    for canal in janela:
        print(canal["canal"], "| Delta:", canal["delta"])

print("\nTeste concluído.")


from validar_sinal.tela.regra_qualidade import decidir_com_qualidade

necessarios = ["EEG Fpz-Cz", "EEG Pz-Oz"]

casos = [
    {
        "nome": "Sem alertas",
        "alertas": [],
        "esperado": "valida"
    },
    {
        "nome": "Alerta em canal necessário",
        "alertas": [
            {"canal": "EEG Fpz-Cz", "motivo": "canal_constante"}
        ],
        "esperado": "suspensa"
    },
    {
        "nome": "Alerta em canal não necessário",
        "alertas": [
            {"canal": "EEG F3", "motivo": "canal_constante"}
        ],
        "esperado": "valida"
    }
]

print("\nTESTES DA REGRA DE QUALIDADE")

for caso in casos:
    resultado = decidir_com_qualidade(
        caso["alertas"],
        necessarios,
        "valida"
    )

    status = "PASSOU" if resultado == caso["esperado"] else "FALHOU"

    print(
        caso["nome"],
        "| esperado:", caso["esperado"],
        "| recebido:", resultado,
        "|", status
    )
