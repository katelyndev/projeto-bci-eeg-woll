
import numpy as np
import matplotlib.pyplot as plt
import mne
import warnings

from sklearn.exceptions import ConvergenceWarning


def processar_ica(
    dados_eeg,
    frequencia,
    nomes_canais=None,
    aplicar_filtro=True
):
    """
    Executa a ICA nos sinais EEG.

    dados_eeg: matriz (canais, amostras) em µV.
    frequencia: frequência de amostragem em Hz.
    nomes_canais: nomes opcionais dos eletrodos.
    aplicar_filtro: aplica filtro de 1 a 40 Hz
                    quando os dados ainda não
                    foram filtrados.

    Retorna:
        componentes
        modelo_ica
    """

    dados_eeg = np.asarray(
        dados_eeg,
        dtype=float
    )

    if dados_eeg.ndim != 2:
        raise ValueError(
            "Formato inválido. Esperado: "
            "(canais, amostras)."
        )

    quantidade_canais, quantidade_amostras = (
        dados_eeg.shape
    )

    if quantidade_canais < 2:
        raise ValueError(
            "A ICA precisa de pelo menos 2 canais."
        )

    if quantidade_amostras < 2:
        raise ValueError(
            "A gravação precisa de pelo menos 2 amostras."
        )

    if not np.all(np.isfinite(dados_eeg)):
        raise ValueError(
            "O EEG contém valores inválidos."
        )

    if not np.isfinite(frequencia) or frequencia <= 0:
        raise ValueError(
            "Frequência de amostragem inválida."
        )

    if aplicar_filtro and frequencia <= 80:
        raise ValueError(
            "A frequência deve ser maior que 80 Hz "
            "para aplicar o filtro de 40 Hz."
        )

    if nomes_canais is None:
        nomes_canais = [
            f"Ch{i + 1}"
            for i in range(quantidade_canais)
        ]

    if len(nomes_canais) != quantidade_canais:
        raise ValueError(
            "Quantidade de nomes incompatível "
            "com os canais EEG."
        )

    info = mne.create_info(
        ch_names=nomes_canais,
        sfreq=frequencia,
        ch_types="eeg"
    )

    # Converter microvolts para volts
    dados_volts = dados_eeg * 1e-6

    raw = mne.io.RawArray(
        dados_volts,
        info,
        verbose=False
    )

    # Aplicar filtro apenas quando solicitado
    if aplicar_filtro:
        raw_processado = raw.copy().filter(
            l_freq=1.0,
            h_freq=40.0,
            verbose=False
        )
    else:
        raw_processado = raw.copy()

    # Configuração da ICA
    modelo_ica = mne.preprocessing.ICA(
        n_components=quantidade_canais,
        method="fastica",
        random_state=97,
        max_iter=3000
    )

    # Executar ICA e registrar avisos
    with warnings.catch_warnings(
        record=True
    ) as avisos:

        warnings.simplefilter(
            "always",
            ConvergenceWarning
        )

        modelo_ica.fit(
            raw_processado,
            verbose=False
        )

    houve_aviso = any(
        issubclass(
            aviso.category,
            ConvergenceWarning
        )
        for aviso in avisos
    )

    modelo_ica.houve_aviso_convergencia = (
        houve_aviso
    )

    # Extrair componentes independentes
    componentes = modelo_ica.get_sources(
        raw_processado
    ).get_data()

    return componentes, modelo_ica


def reconstruir_eeg(
    dados_eeg,
    frequencia,
    modelo_ica,
    componentes_excluir=None,
    nomes_canais=None,
    aplicar_filtro=True
):
    """
    Reconstrói o sinal EEG após a ICA.

    Se componentes_excluir estiver vazio,
    nenhum componente será removido.

    Retorna o EEG em microvolts.
    """

    dados_eeg = np.asarray(
        dados_eeg,
        dtype=float
    )

    if dados_eeg.ndim != 2:
        raise ValueError(
            "Os dados devem ter formato "
            "(canais, amostras)."
        )

    quantidade_canais = dados_eeg.shape[0]

    if nomes_canais is None:
        nomes_canais = [
            f"Ch{i + 1}"
            for i in range(quantidade_canais)
        ]

    if len(nomes_canais) != quantidade_canais:
        raise ValueError(
            "Quantidade de nomes incompatível."
        )

    info = mne.create_info(
        ch_names=nomes_canais,
        sfreq=frequencia,
        ch_types="eeg"
    )

    raw = mne.io.RawArray(
        dados_eeg * 1e-6,
        info,
        verbose=False
    )

    if aplicar_filtro:
        raw_processado = raw.copy().filter(
            l_freq=1.0,
            h_freq=40.0,
            verbose=False
        )
    else:
        raw_processado = raw.copy()

    if componentes_excluir is None:
        componentes_excluir = []

    raw_reconstruido = modelo_ica.apply(
        raw_processado.copy(),
        exclude=list(componentes_excluir),
        verbose=False
    )

    return (
        raw_reconstruido.get_data() * 1e6
    )


def identificar_componente_simulado(
    componentes,
    piscadas
):
    """
    Identifica o componente mais correlacionado
    com as piscadas do simulador.
    """

    correlacoes = []

    for componente in componentes:

        correlacao = np.corrcoef(
            componente,
            piscadas
        )[0, 1]

        if np.isfinite(correlacao):
            correlacoes.append(
                abs(correlacao)
            )
        else:
            correlacoes.append(0.0)

    return int(
        np.argmax(correlacoes)
    )


def validar_correlacao(
    componentes,
    piscadas
):
    """
    Validação numérica usando o simulador.
    """

    correlacoes = []

    print("\nVALIDAÇÃO NUMÉRICA DA ICA")
    print("-" * 45)

    for i, componente in enumerate(componentes):

        correlacao = np.corrcoef(
            componente,
            piscadas
        )[0, 1]

        if not np.isfinite(correlacao):
            correlacao = 0.0

        correlacao = abs(correlacao)

        correlacoes.append(correlacao)

        print(
            f"ICA {i}: correlação absoluta = "
            f"{correlacao:.4f}"
        )

    indice = int(
        np.argmax(correlacoes)
    )

    melhor_correlacao = correlacoes[indice]

    print("\nRESULTADO DA VALIDAÇÃO")
    print("-" * 45)

    print(
        "Componente mais correlacionado:",
        indice
    )

    print(
        f"Maior correlação absoluta: "
        f"{melhor_correlacao:.4f}"
    )

    return indice, melhor_correlacao


def verificar_convergencia(modelo_ica):
    """
    Verifica a convergência da FastICA.
    """

    print("\nVERIFICAÇÃO DA CONVERGÊNCIA")
    print("-" * 45)

    iteracoes = modelo_ica.n_iter_
    limite = modelo_ica.max_iter

    houve_aviso = getattr(
        modelo_ica,
        "houve_aviso_convergencia",
        False
    )

    print(
        "Iterações realizadas:",
        iteracoes
    )

    print(
        "Limite máximo de iterações:",
        limite
    )

    print(
        "Aviso de não convergência:",
        "SIM" if houve_aviso else "NÃO"
    )

    if not houve_aviso and iteracoes < limite:
        print(
            "\nRESULTADO: sem indícios "
            "de falha de convergência."
        )

        return True

    print(
        "\nRESULTADO: convergência "
        "não confirmada."
    )

    return False


def executar_ica():
    """
    Mantém a compatibilidade com detector.py.
    """

    from simulador import obter_dados

    dados_eeg, frequencia, tempo = (
        obter_dados()
    )

    componentes, modelo_ica = processar_ica(
        dados_eeg,
        frequencia,
        aplicar_filtro=True
    )

    return componentes, tempo, frequencia


if __name__ == "__main__":

    from simulador import obter_dados, piscadas

    dados_eeg, frequencia, tempo = (
        obter_dados()
    )

    componentes, modelo_ica = processar_ica(
        dados_eeg,
        frequencia,
        aplicar_filtro=True
    )

    indice = identificar_componente_simulado(
        componentes,
        piscadas
    )

    print("\nICA EXECUTADA COM SUCESSO!")

    print(
        "Quantidade de componentes:",
        len(componentes)
    )

    print(
        "Componente ocular candidato:",
        indice
    )

    validar_correlacao(
        componentes,
        piscadas
    )

    verificar_convergencia(
        modelo_ica
    )

    fig, axes = plt.subplots(
        len(componentes),
        1,
        figsize=(12, 12),
        sharex=True
    )

    for i, componente in enumerate(componentes):

        axes[i].plot(
            tempo,
            componente
        )

        axes[i].set_ylabel(
            f"ICA {i}"
        )

        axes[i].grid(True)

    axes[-1].set_xlabel(
        "Tempo (s)"
    )

    plt.tight_layout()

    plt.savefig(
        "resultado_ica.png",
        dpi=150
    )

    plt.close()

    print(
        "\nGráfico salvo em resultado_ica.png"
    )
