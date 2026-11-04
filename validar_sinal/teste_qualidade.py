import numpy as np

from qualidade import validar_qualidade


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