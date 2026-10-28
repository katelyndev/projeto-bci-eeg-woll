"""Valida remoção de piscadas conhecidas, reutilizando o simulador do Matheus."""
import argparse
import importlib.util
import json

import numpy as np
from scipy.signal import butter, sosfiltfilt

from analise_beta import calcular_beta
from teste_ica_beta import PASTA, importar_ica


def filtrar(sinal, fs):
    # Mesmo tipo de filtro usado no teste real, respeitando o fs do simulador.
    sinal = sinal - sinal.mean(axis=-1, keepdims=True)
    filtro = butter(4, (1, 40), btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(filtro, sinal, axis=-1)


def executar(semente):
    caminho = PASTA.parent / "ica" / "simulador.py"
    spec = importlib.util.spec_from_file_location("simulador_do_projeto", caminho)
    simulador = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(simulador)
    ica = importar_ica()

    # Mesma semente: mesmas fontes aleatórias e mistura; só a piscada muda.
    com_piscadas, fs, tempo, piscadas = simulador.gerar_cenario(
        intensidade_piscadas=1.0, semente=semente)
    sem_piscadas, fs_ref, tempo_ref, _ = simulador.gerar_cenario(
        intensidade_piscadas=0.0, semente=semente)
    if fs != fs_ref or not np.array_equal(tempo, tempo_ref):
        raise RuntimeError("As duas simulações não são comparáveis.")
    if com_piscadas.shape != sem_piscadas.shape or np.allclose(com_piscadas, sem_piscadas):
        raise RuntimeError("Simulações inválidas ou sem interferência.")

    referencia = filtrar(sem_piscadas, fs)
    contaminado = filtrar(com_piscadas, fs)
    piscadas_filtradas = filtrar(piscadas, fs)
    componentes, modelo = ica.processar_ica(contaminado, fs, aplicar_filtro=False)
    if not ica.verificar_convergencia(modelo):
        raise RuntimeError("ICA não convergiu; não interpretar como validação.")
    controle = ica.reconstruir_eeg(contaminado, fs, modelo, [], aplicar_filtro=False)
    if not np.allclose(controle, contaminado, rtol=1e-6, atol=1e-6):
        raise RuntimeError("Reconstrução sem exclusões não preservou o sinal.")

    # Aqui conhecemos a piscada. Esta seleção não deve ser copiada para o EEG real.
    indice = ica.identificar_componente_simulado(componentes, piscadas_filtradas)
    correlacao = abs(float(np.corrcoef(componentes[indice], piscadas_filtradas)[0, 1]))
    reconstruido = ica.reconstruir_eeg(contaminado, fs, modelo, [indice], aplicar_filtro=False)
    if not np.isfinite(reconstruido).all():
        raise RuntimeError("Reconstrução inválida.")

    erro_antes = float(np.sqrt(np.mean((contaminado-referencia)**2)))
    erro_depois = float(np.sqrt(np.mean((reconstruido-referencia)**2)))
    reducao_erro = 100 * (1-erro_depois/erro_antes) if erro_antes > 0 else None
    # Canal simulado 1 é apenas um exemplo de beta; o erro acima usa todos os canais.
    betas = {nome: float(calcular_beta(dados[0], fs)[2]) for nome, dados in (
        ("referencia_sem_piscadas", referencia), ("com_piscadas", contaminado),
        ("apos_ica", reconstruido))}
    print(f"\nSimulação: semente {semente}, {len(contaminado)} canais, {fs} Hz, {tempo[-1]+1/fs:.0f} s.")
    print(f"Componente selecionado pela piscada conhecida: IC {indice}")
    print(f"Correlação absoluta com a piscada: {correlacao:.4f}")
    print(f"Erro em relação à referência: {erro_antes:.4f} -> {erro_depois:.4f} µV")
    if reducao_erro is not None:
        print(f"Redução do erro RMS: {reducao_erro:.2f}% (não é porcentagem de concentração)")
    print("Beta absoluto do canal simulado 1 (µV²):")
    for nome, beta in betas.items():
        print(f"  {nome}: {beta:.4f}")

    destino = PASTA / "resultados_ica" / "simulacao"
    destino.mkdir(parents=True, exist_ok=True)
    relatorio = {"semente": semente, "fs": fs, "canais": len(contaminado),
                 "componente_excluido": indice, "correlacao_piscada": correlacao,
                 "erro_rms_antes_uv": erro_antes, "erro_rms_depois_uv": erro_depois,
                 "reducao_erro_percentual": reducao_erro, "beta_canal1_uv2": betas}
    (destino / f"validacao_semente{semente}.json").write_text(
        json.dumps(relatorio, indent=2), encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, eixos = plt.subplots(2, 1, figsize=(12, 7))
    for dados, rotulo, cor in ((contaminado, "Com piscadas", "tab:orange"),
                               (reconstruido, "Após ICA", "tab:green"),
                               (referencia, "Referência sem piscadas", "tab:blue")):
        eixos[0].plot(tempo, dados[0], label=rotulo, color=cor, lw=.9)
        trecho = (tempo >= 8) & (tempo < 10)
        eixos[1].plot(tempo[trecho], dados[0, trecho], label=rotulo, color=cor, lw=.9)
    eixos[0].set_title("Canal simulado 1 — comparação com referência conhecida")
    eixos[1].set_title("Ampliação da piscada próxima de 9 segundos")
    for eixo in eixos:
        eixo.set_xlabel("Tempo (s)")
        eixo.set_ylabel("µV")
        eixo.grid(alpha=.25)
        eixo.legend()
    fig.tight_layout()
    fig.savefig(destino / f"validacao_semente{semente}.png", dpi=140)
    plt.close(fig)
    print(f"Gráfico e relatório salvos em: {destino}")
    print("Referência sem piscadas mantém as demais fontes e ruídos do simulador.")
    print("Resultado restrito à simulação; não identifica o evento real dos 13 segundos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semente", type=int, nargs="+", default=[42])
    for semente in dict.fromkeys(parser.parse_args().semente):
        executar(semente)
