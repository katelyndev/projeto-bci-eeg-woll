from validar_sinal.ler_gravacao import preparar_gravacao
from validar_sinal.tela.regra_qualidade import decidir_com_qualidade


janelas = preparar_gravacao(
    arquivo="beta_concentracao/S003E01.edf",
    duracao_segundos=60,
    canais=[
        "AF3", "F7", "F3", "FC5", "T7", "P7", "O1",
        "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"
    ],
    segundos_por_janela=4
)

casos = [
    ("P8 com problema, somente F3 necessário",
     janelas[0], ["F3"], "permitido_teste"),

    ("P8 com problema e necessário",
     janelas[0], ["F3", "P8"], "sem_decisao"),

    ("Janela seguinte sem alertas",
     janelas[2], ["F3", "P8"], "permitido_teste")
]

for descricao, janela, necessarios, esperado in casos:
    resultado = decidir_com_qualidade(
        janela["alertas"],
        necessarios,
        "permitido_teste"
    )

    print(f"\n{descricao}")
    print(f"Trecho: {janela['inicio']}–{janela['fim']} s")
    print("Resultado:", resultado)

    assert resultado == esperado, (
        f"Esperado: {esperado}; recebido: {resultado}"
    )

print("\nOs três casos de integração passaram.")