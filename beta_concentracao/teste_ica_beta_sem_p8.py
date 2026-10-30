"""Teste separado do efeito do ICA: filtro igual, com e sem exclusões revisadas.

Primeiro: python beta_concentracao/teste_ica_beta.py --pessoa 1
Depois da revisão: acrescente --etapa comparar.
Não requer os patches anteriores e não altera os arquivos de gravação.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt, welch

from analise_beta import calcular_beta, calcular_beta_relativo

PASTA = Path(__file__).resolve().parent
FS = 256
# Ordem confirmada no cabeçalho EDF. Os CSV novos contêm apenas os canais EEG.
# As 14 colunas que existem no CSV original.
CANAIS_ARQUIVO = [
    "AF3", "F7", "F3", "FC5", "T7", "P7", "O1",
    "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"
]

# Os 13 canais que vamos usar neste teste.
CANAIS = [
    nome for nome in CANAIS_ARQUIVO
    if nome != "P8"
]
CONDICOES = (("Relax1", "relax1"), ("Foco", "foco"), ("Relax2", "relax2"))


def importar_ica():
    # Carrega as funções do Matheus sem executar seu simulador.
    caminho = PASTA.parent / "ica" / "ica.py"
    spec = importlib.util.spec_from_file_location("ica_do_projeto", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def ler_e_filtrar(caminho):
    # Mesmo formato do BrainFlow: no disco, uma amostra por linha.
    tabela = np.loadtxt(caminho, ndmin=2)
    if tabela.shape != (60 * FS, len(CANAIS_ARQUIVO)):
        raise ValueError("Esperado CSV novo: 15360 amostras e 14 canais, sem contador/tempo.")
    if not np.isfinite(tabela).all():
        raise ValueError("A gravação contém valores inválidos.")
    indices = [
        CANAIS_ARQUIVO.index(nome)
        for nome in CANAIS
    ]

    eeg = np.ascontiguousarray(tabela[:, indices].T)
    # Retira o deslocamento constante de cada canal.
    eeg -= eeg.mean(axis=1, keepdims=True)
    # Filtra a gravação inteira antes do recorte em janelas.
    filtro = butter(4, (1, 40), btype="bandpass", fs=FS, output="sos")
    eeg = sosfiltfilt(filtro, eeg, axis=1)
    if not np.isfinite(eeg).all() or np.linalg.matrix_rank(eeg) < len(CANAIS):
        raise ValueError("Canais inválidos ou dependentes; revisar antes de usar 14 componentes.")
    return eeg


def validar_exclusoes(indices, quantidade):
    if (not isinstance(indices, list)
            or any(type(i) is not int or not 0 <= i < quantidade for i in indices)
            or len(set(indices)) != len(indices) or len(indices) == quantidade):
        raise ValueError("Use índices inteiros únicos, começando em 0, sem excluir todos.")


def medir(sinal):
    # Mantém os cálculos do analise_beta.py atual e as janelas de 4 segundos.
    sinal = sinal[:60 * FS]
    _, _, total = calcular_beta(sinal, FS)
    absoluto, relativo = [], []
    for inicio in range(0, len(sinal), 4 * FS):
        f, psd, beta = calcular_beta(sinal[inicio:inicio + 4 * FS], FS)
        absoluto.append(float(beta))
        relativo.append(calcular_beta_relativo(f, psd))
    return float(total), absoluto, relativo


def salvar_graficos(componentes, modelo, antes, depois, canal, destino, nome):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Componentes são misturas estimadas; não correspondem a eletrodos.
    quantidade = len(componentes)
    fig, eixos = plt.subplots(quantidade, 2, figsize=(13, 2 * quantidade))
    tempo = np.arange(componentes.shape[1]) / FS
    for i in range(quantidade):
        eixos[i, 0].plot(tempo[::5], componentes[i, ::5], lw=.5)
        eixos[i, 0].set_ylabel(f"IC {i}")
        f, p = welch(componentes[i], fs=FS, nperseg=2 * FS)
        faixa = (f >= 1) & (f <= 40)
        eixos[i, 1].semilogy(f[faixa], p[faixa])
    eixos[0, 0].set_title("Componentes no tempo — escala arbitrária")
    eixos[0, 1].set_title("Distribuição de potência dos componentes")
    eixos[-1, 0].set_xlabel("Tempo (s); traçado exibido a cada 5 amostras")
    eixos[-1, 1].set_xlabel("Hz")
    fig.tight_layout()
    fig.savefig(destino / f"{nome}_componentes.png", dpi=110)
    plt.close(fig)

    fig, eixos = plt.subplots(1, 2, figsize=(13, 4))
    pesos = modelo.get_components()
    pesos = pesos / np.max(np.abs(pesos), axis=0, keepdims=True)
    eixos[0].imshow(pesos, cmap="RdBu_r", vmin=-1, vmax=1)
    eixos[0].set_yticks(range(len(CANAIS)), CANAIS)
    eixos[0].set_xticks(range(quantidade), [f"IC {i}" for i in range(quantidade)], rotation=55, ha="right")
    eixos[0].set_title("Pesos normalizados; ordem esperada dos canais")
    for valores, rotulo in ((antes, "Só filtro inicial"), (depois, "Após reconstrução ICA")):
        f, p = welch(valores[canal, :60*FS], fs=FS, nperseg=2*FS)
        faixa = (f >= 1) & (f <= 40)
        eixos[1].semilogy(f[faixa], p[faixa], label=rotulo)
    eixos[1].set_title(f"PSD de {CANAIS[canal]} — primeiros 60 s")
    eixos[1].set_xlabel("Hz")
    eixos[1].legend()
    fig.tight_layout()
    fig.savefig(destino / f"{nome}_pesos_psd.png", dpi=130)
    plt.close(fig)

    # Mesmo canal e mesmas amostras: enxergar o efeito da exclusão no tempo.
    # O processamento continua usando o minuto completo; só o gráfico é ampliado.
    fig, eixos = plt.subplots(3, 1, figsize=(13, 10))
    for valores, rotulo in ((antes, "Só filtro inicial"), (depois, "Após reconstrução ICA")):
        eixos[0].plot(tempo, valores[canal], lw=.7, label=rotulo)
        trecho = (tempo >= 10) & (tempo < 16)
        eixos[1].plot(tempo[trecho], valores[canal, trecho], lw=.9, label=rotulo)
    # O que mudou é mostrado separadamente; não chamamos toda a diferença de ruído.
    eixos[2].plot(tempo, antes[canal]-depois[canal], color="tab:green", lw=.7)
    eixos[0].set_title(f"{CANAIS[canal]} — minuto completo, antes e depois do ICA")
    eixos[1].set_title("Mesmo sinal — ampliação entre 10 e 16 segundos")
    eixos[2].set_title("Diferença antes − depois; origem da contribuição ainda não confirmada")
    for eixo in eixos:
        eixo.set_xlabel("Tempo dentro do minuto (s)")
        eixo.set_ylabel("µV")
        eixo.grid(alpha=.25)
    eixos[0].legend()
    eixos[1].legend()
    fig.tight_layout()
    fig.savefig(destino / f"{nome}_tempo.png", dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pessoa", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--sessao", type=int, choices=(1, 2), default=1)
    parser.add_argument("--canal", choices=CANAIS, default="F3")
    parser.add_argument("--etapa", choices=("revisar", "comparar"), default="revisar")
    parser.add_argument(
        "--exportar",
        action="store_true",
        help="Salva os sinais antes e depois da exclusão pelo ICA."
    )
    args = parser.parse_args()
    if args.sessao == 1:
        nome_saida = f"pessoa{args.pessoa}"
    else:
        nome_saida = f"pessoa{args.pessoa}_E02"

    nome_saida = f"{nome_saida}_sem_P8"
    destino = PASTA / "resultados_ica" / "concentracao256" / nome_saida
    destino.mkdir(parents=True, exist_ok=True)
    caminho_config = destino / "exclusoes.json"
    configuracao = json.loads(caminho_config.read_text()) if caminho_config.exists() else {}
    if args.etapa == "comparar" and not configuracao:
        parser.error("Execute a etapa revisar primeiro.")
    ica = importar_ica()
    canal = CANAIS.index(args.canal)
    resumo, janelas, propostas = [], [], {}
    print(f"Pessoa S{args.pessoa:03d}E{args.sessao:02d}; {FS} Hz; canal {args.canal}; 60 s; janelas de 4 s.")
    print(
        f"Comparação offline: {len(CANAIS)} canais recebem "
        "o mesmo filtro inicial de 1–40 Hz; P8 não utilizado."
    )
    print("Relax1 = olhos abertos; Foco = tarefa; Relax2 = olhos fechados (condições separadas).")
    for condicao, prefixo in CONDICOES:
        caminho = PASTA / f"gravacao_concentracao_{prefixo}_S{args.pessoa:03d}E{args.sessao:02d}.csv"
        eeg = ler_e_filtrar(caminho)
        # O conversor lê as amplitudes físicas do EDF em microvolts.
        # As funções do Matheus convertem para volts e retornam microvolts.
        componentes, modelo = ica.processar_ica(eeg, FS, nomes_canais=CANAIS, aplicar_filtro=False)
        if not ica.verificar_convergencia(modelo):
            raise RuntimeError(f"ICA não convergiu em {condicao}; não comparar exclusões.")
        assinatura = hashlib.sha256(np.round(modelo.get_components(), 10).tobytes()).hexdigest()
        regra_base = {"arquivo": caminho.name, "sha256": hashlib.sha256(caminho.read_bytes()).hexdigest(),
                      "modelo_sha256": assinatura, "excluir": [], "justificativa": ""}
        propostas[condicao] = regra_base
        controle = ica.reconstruir_eeg(eeg, FS, modelo, componentes_excluir=[],
                                     nomes_canais=CANAIS, aplicar_filtro=False)
        if not np.allclose(eeg, controle, rtol=1e-6, atol=1e-6):
            raise RuntimeError("Reconstrução sem exclusões alterou o sinal além da tolerância.")
        excluir = []
        if args.etapa == "comparar":
            regra = configuracao.get(condicao, {})
            for chave in ("arquivo", "sha256", "modelo_sha256"):
                if regra.get(chave) != regra_base[chave]:
                    raise ValueError(f"Arquivo/modelo mudou em {condicao}; faça uma nova revisão.")
            excluir = regra.get("excluir")
            validar_exclusoes(excluir, len(componentes))
            if excluir and not str(regra.get("justificativa", "")).strip():
                raise ValueError("Descreva a evidência de artefato em justificativa.")
        depois = ica.reconstruir_eeg(eeg, FS, modelo, componentes_excluir=excluir,
                                   nomes_canais=CANAIS, aplicar_filtro=False) if excluir else controle
        if depois.shape != eeg.shape or not np.isfinite(depois).all():
            raise RuntimeError("Reconstrução inválida.")
        if args.exportar and args.etapa == "comparar":
            pasta_exportacao = destino / "gravacoes_comparacao"

            for versao, sinal in (
                ("antes_ica", eeg),
                ("depois_ica", depois)
            ):
                pasta_versao = pasta_exportacao / versao
                pasta_versao.mkdir(parents=True, exist_ok=True)

                arquivo_saida = pasta_versao / caminho.name

                np.savetxt(
                    arquivo_saida,
                    sinal.T,
                    delimiter="\t",
                    fmt="%.17g"
                )

                print(f"Gravação salva: {arquivo_saida}")
        total_antes, beta_antes, relativo_antes = medir(eeg[canal])
        total_depois, beta_depois, relativo_depois = medir(depois[canal])
        variacao = 100*(total_depois-total_antes)/total_antes if total_antes > 0 else None
        rms = float(np.sqrt(np.mean((depois-eeg)**2)))
        print(f"\n{condicao}: componentes excluídos = {excluir}")
        print(f"Beta absoluto: {total_antes:.4f} -> {total_depois:.4f} µV²")
        print(f"Variação da potência beta: {variacao:.2f}%" if variacao is not None else "Variação indefinida: beta inicial zero.")
        print(f"Mediana beta relativo: {np.median(relativo_antes):.2f}% -> {np.median(relativo_depois):.2f}%")
        print(
            f"Diferença RMS nos {len(CANAIS)} canais: "
            f"{rms:.8g} µV; sem exclusões = controle de reconstrução."
        )
        if condicao == "Relax1" and args.etapa == "comparar":
            print("\nAlteração no F3 por trecho:")

            for inicio, fim in ((0, 10), (10, 16), (16, 60)):
                antes_trecho = eeg[canal, inicio * FS:fim * FS]
                depois_trecho = depois[canal, inicio * FS:fim * FS]

                diferenca_rms = np.sqrt(
                    np.mean((antes_trecho - depois_trecho) ** 2)
                )

                amplitude_antes = np.ptp(antes_trecho)
                amplitude_depois = np.ptp(depois_trecho)

                print(
                    f"  {inicio}–{fim} s: "
                    f"diferença RMS = {diferenca_rms:.2f} µV; "
                    f"amplitude pico a pico = "
                    f"{amplitude_antes:.2f} -> "
                    f"{amplitude_depois:.2f} µV"
                )
        resumo.append({"pessoa": args.pessoa, "condicao": condicao, "canal": args.canal,
                       "etapa": args.etapa, "excluir": json.dumps(excluir),
                       "beta_antes": total_antes, "beta_depois": total_depois,
                       "variacao_beta_percentual": variacao, "diferenca_rms_canais_uv": rms,
                       "canais_utilizados": ",".join(CANAIS),
                       "sessao": args.sessao,  
                       "mediana_relativo_antes": float(np.median(relativo_antes)),
                       "mediana_relativo_depois": float(np.median(relativo_depois)),
                       "arquivo_sha256": regra_base["sha256"], "modelo_sha256": assinatura,
                       "justificativa": configuracao.get(condicao, {}).get("justificativa", "") if excluir else ""})
        for i in range(len(beta_antes)):
            janelas.append({"condicao": condicao, "janela": i+1, "inicio_s": 4*i,
                            "beta_antes": beta_antes[i], "beta_depois": beta_depois[i],
                            "relativo_antes": relativo_antes[i], "relativo_depois": relativo_depois[i]})
        salvar_graficos(componentes, modelo, eeg, depois, canal, destino, f"{prefixo}_{args.etapa}_{args.canal}")
    if not caminho_config.exists():
        caminho_config.write_text(json.dumps(propostas, indent=2, ensure_ascii=False), encoding="utf-8")
    for nome, registros in (("resumo", resumo), ("janelas", janelas)):
        with (destino / f"{nome}_{args.etapa}_{args.canal}.csv").open("w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=list(registros[0]))
            escritor.writeheader()
            escritor.writerows(registros)
    print(f"\nResultados e configuração em: {destino}")
    print("Nenhum CSV original foi alterado. Potência menor não comprova limpeza melhor.")
    if args.etapa == "revisar":
        print("Próximo passo: revisar componentes e registrar exclusões justificadas em exclusoes.json.")


if __name__ == "__main__":
    main()
