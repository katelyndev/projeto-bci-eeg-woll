import numpy as np

from validar_sinal.qualidade import validar_qualidade


nomes_canais = ["F3", "P8", "F4"]

dados = np.array([
    [1.0, 2.0, 3.0, 2.0],
    [5.0, 5.0, 5.0, 5.0],
    [1.0, np.nan, 2.0, 3.0]
])

problemas = validar_qualidade(dados, nomes_canais)

print("Problemas encontrados:")

for problema in problemas:
    print(f"{problema['canal']}: {problema['motivo']}")


dados_sem_problemas = np.array([
    [1.0, 2.0, 3.0, 2.0],
    [5.0, 6.0, 5.0, 4.0],
    [1.0, 3.0, 2.0, 3.0]
])

resultado = validar_qualidade(dados_sem_problemas, nomes_canais)

print("\nTeste sem problemas previstos:")
print(resultado)

dados_com_infinito = np.array([
    [1.0, np.inf, 3.0, 2.0]
])

resultado = validar_qualidade(dados_com_infinito, ["F3"])

print("\nTeste com infinito:")
print(resultado)

print("\nTeste com quantidade incorreta de nomes:")

try:
    validar_qualidade(
        np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ]),
        ["F3"]
    )
except ValueError as erro:
    print("Erro identificado:", erro)
else:
    raise AssertionError("A entrada incorreta foi aceita.")

print("\nTeste com janela vazia:")

try:
    validar_qualidade(
        np.empty((1, 0)),
        ["F3"]
    )
except ValueError as erro:
    print("Erro identificado:", erro)
else:
    raise AssertionError("A janela vazia foi aceita.")

print("\nTeste com dados em uma dimensão:")

try:
    validar_qualidade(
        np.array([1.0, 2.0, 3.0]),
        ["F3"]
    )
except ValueError as erro:
    print("Erro identificado:", erro)
else:
    raise AssertionError("Os dados em uma dimensão foram aceitos.")