from interface_web.decisao_olhos import iniciar_simulacao_continua

# função de exemplo, só pra simular o que o Pedro faria
def atualizar_luz(estado):
    if estado == 1:
        print("🟢 Verde (fechado)")
    else:
        print("🔴 Vermelho (aberto)")

# chama a simulação, com delay curto só pra testar rápido
iniciar_simulacao_continua(atualizar_luz, delay=1)