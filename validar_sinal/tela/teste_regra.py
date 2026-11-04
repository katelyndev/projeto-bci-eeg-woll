# TESTE DA REGRA DE QUALIDADE
# roda casos fixos e confere se a função devolve o resultado esperado

# traz a função decidir_com_qualidade do arquivo regra_qualidade.py
from regra_qualidade import decidir_com_qualidade

# caso 1: sem alertas, a decisão normal vale
resultado = decidir_com_qualidade([], ["F3"], "focado")
print("caso 1:", resultado, "| esperado: focado")

# caso 2: alerta num canal que a análise não usa, a decisão normal ainda vale
resultado = decidir_com_qualidade([{"canal": "P8", "motivo": "constante"}], ["F3"], "focado")
print("caso 2:", resultado, "| esperado: focado")

# caso 3: alerta num canal que a análise usa, a decisão é suspensa
resultado = decidir_com_qualidade([{"canal": "F3", "motivo": "constante"}], ["F3"], "focado")
print("caso 3:", resultado, "| esperado: sem_decisao")

# caso 4: valor inválido num canal usado, a decisão é suspensa mesmo com outra decisão normal
resultado = decidir_com_qualidade([{"canal": "F3", "motivo": "invalido"}], ["F3"], "relaxado")
print("caso 4:", resultado, "| esperado: sem_decisao")