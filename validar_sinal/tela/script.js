// mostra as janelas de exemplo uma de cada vez 
// lê o arquivo exemplos_teste_tela.json e atualiza a tela a cada 3 segundos

// arquivo de dados que a tela lê; troque aqui para usar outra fonte
// const ARQUIVO_DADOS = "janelas_reais.json"; 
// const ARQUIVO_DADOS = "exemplos_sono_teste.json"; 
const ARQUIVO_DADOS = "janelas_sono_SC4001E0.json";
// const ARQUIVO_DADOS = "janelas_sono_SC4011E0.json";


// cria a variavel janelas e comeca ela com uma lista vazia []
let janelas = [];

// pocisao da janela so serve para mostras se é a primeira ...
let posicao = 0;

// funcao que le os arquivos de exeplo e guarda as janelas 
async function carregar(){
    // pede ao servidor o arquivo json e quarda a resposta em uma variavel
    const resposta = await fetch(ARQUIVO_DADOS);
    // pega a resposta que chegou do servidor e transforma na lista de janelas e assim guardando na variavel janelas
    janelas = await resposta.json();
}

// traduz o estado do arquivo para o texto qua aparece para o usuario 
function textoDoEstado(estado){
    // se o estado recebido for exatamente igual a "focado" sendo exatamente igual retorna 
    if(estado === "focado") return "Focado"; 
    if(estado === "relaxado") return "Relaxado";
    // "aguardando" = ainda não há análise para esta janela; não é problema no sinal
    if (estado === "aguardando") return "Aguardando análise";
    if (estado === "valida") return "Válida";
    if (estado === "suspensa") return "Suspenso (problema no sinal)";

    return "Sem decisão - problema no sinal";
}

//  traduz o motivo do arquivo para o texto que vai aparecer para o usuario 
function textoDoMotivo(motivo){
    if (motivo === "canal_constante") return "Canal travado";
    if (motivo === "valor_invalido") return "Valor inválido";

    // se nenhum das alternativas acima volta o conteudo original
    return motivo;
}

// troca o estado técnico pela palavra que aparece no cartão
function rotuloDoCartao(estado) {
    if (estado === "ok") return "ok";
    if (estado === "aviso") return "AVISO";
    return "BLOQUEIO";
}

// desenha um cartão para cada canal, com a cor de acordo com os alertas da janela
function desenharGrade(janela) {
    // pega a caixa da grade na página
    const grade = document.getElementById("grade");
    // apaga os cartões da janela anterior
    grade.innerHTML = "";
    // mostra o nome do arquivo que está sendo lido, para não confundir os participantes
    document.getElementById("arquivo").textContent = "Arquivo: " + ARQUIVO_DADOS;

    // para cada canal da lista, na ordem em que ela vem
    janela.canais.forEach((canal) => {
        // procura os alertas que pertencem a esse canal
        const alertasDoCanal = janela.alertas.filter((alerta) => alerta.canal === canal);

        // começa supondo que o canal está sem problema
        let estado = "ok";

        // se houver algum alerta nesse canal, muda o estado
        if (alertasDoCanal.length > 0) {
            // se o canal é usado pela análise, bloqueia; se não, só avisa
            estado = janela.necessarios.includes(canal) ? "bloqueio" : "aviso";
        }

        // cria um elemento novo para o cartão
        const cartao = document.createElement("div");
        // dá ao cartão a classe "cartao" e a classe do estado, por exemplo "cartao bloqueio"
        cartao.className = "cartao " + estado;
        // monta o cartão com nome e situação
        cartao.innerHTML = "<strong>" + canal + "</strong><span>" + rotuloDoCartao(estado) + "</span>";
        // coloca o cartão dentro da grade
        grade.appendChild(cartao);
    });
}


// Desenha a tabela com as potências dos canais da janela atual.
function desenharPotencias(janela) {

    // Localiza no HTML o espaço reservado para a tabela.
    const area = document.getElementById("potencias");

    // Limpa os valores da janela anterior.
    area.innerHTML = "";

    // Obtém a lista de potências da janela atual.
    const potencias = janela.potencias;

    // Verifica se existem potências disponíveis nesta janela.
    if (!Array.isArray(potencias) || potencias.length === 0) {

        // Cria uma mensagem para informar que não há dados disponíveis.
        const mensagem = document.createElement("p");

        // Define o texto da mensagem.
        mensagem.textContent = "Não há potências disponíveis para esta janela.";

        // Exibe a mensagem na página.
        area.appendChild(mensagem);

        // Encerra a função, pois não há dados para montar a tabela.
        return;
    }

    // Cria a tabela que apresentará os valores.
    const tabela = document.createElement("table");

    // Cria o cabeçalho da tabela.
    const cabecalho = document.createElement("tr");

    // Define os títulos das colunas e suas unidades.
    const colunas = [
        "Canal",
        "Delta (uV²)",
        "Theta (uV²)",
        "Alfa (uV²)",
        "Beta (uV²)"
    ];

    // Percorre os títulos para criar as células do cabeçalho.
    colunas.forEach((titulo) => {

        // Cria uma célula de cabeçalho.
        const celula = document.createElement("th");

        // Escreve o título da coluna.
        celula.textContent = titulo;

        // Adiciona a célula ao cabeçalho.
        cabecalho.appendChild(celula);
    });

    // Cria a área de cabeçalho da tabela.
    const thead = document.createElement("thead");

    // Coloca a linha de títulos dentro do cabeçalho.
    thead.appendChild(cabecalho);

    // Adiciona o cabeçalho à tabela.
    tabela.appendChild(thead);

    // Cria a área que receberá os dados.
    const corpo = document.createElement("tbody");

    // Percorre os registros de potência de cada canal.
    potencias.forEach((registro) => {

        // Cria uma nova linha para o canal.
        const linha = document.createElement("tr");

        // Cria a célula com o nome do canal.
        const celulaCanal = document.createElement("td");

        // Preenche a célula com o nome do canal.
        celulaCanal.textContent = registro.canal;

        // Adiciona o nome do canal à linha.
        linha.appendChild(celulaCanal);

        // Percorre as quatro bandas de frequência.
        ["delta", "theta", "alfa", "beta"].forEach((banda) => {

            // Cria uma célula para o valor da banda.
            const celula = document.createElement("td");

            // Obtém o valor da banda no registro atual.
            const valor = registro[banda];

            // Exibe o valor com duas casas decimais, se for numérico.
            celula.textContent = Number.isFinite(Number(valor))
                ? Number(valor).toFixed(2)
                : "—";

            // Adiciona a célula à linha.
            linha.appendChild(celula);
        });

        // Adiciona a linha do canal ao corpo da tabela.
        corpo.appendChild(linha);
    });

    // Coloca os dados dentro da tabela.
    tabela.appendChild(corpo);

    // Exibe a tabela na página.
    area.appendChild(tabela);
}


// cria a funcao qu vai receber a janela e  abre o bloco todo 
function mostrar(janela){
    // pega o id da pagina e guarda na variavel 
    const quadrado = document.getElementById("quadrado");
    // troca a classe do quadrado pelo estado da janela (focado, relaxado, valida, suspensa ou aguardando)
    quadrado.className = janela.estado;

    // escreve no parágrafo "texto-estado" a frase que corresponde ao estado da janela
    document.getElementById("texto-estado").textContent = textoDoEstado(janela.estado);

    // pega a lista de alertas da pagina e limpa
    const lista = document.getElementById("alertas");
    // apaga os alertas da janela anterior, para não acomular 
    lista.innerHTML = "";

    // percorre cada alerta da janela um de cada vez 
    for (const alerta of janela.alertas){
        // cria um novo item de lista (<li>), que vai ser uma linha de texto na tela
        const item = document.createElement("li");

        // escreve no item o canal, o motivo traduzido e o intervalo do alerta
        item.textContent = alerta.canal + ": " + textoDoMotivo(alerta.motivo)
            + " (" + janela.intervalo[0] + " a " + janela.intervalo[1] + " s)";
        // adiciona o item à lista
        lista.appendChild(item);
        
    }

    // mostra em que janela e em que segundo da gravação estamos
    document.getElementById("posicao").textContent =
    "Janela " + janela.janela + " de " + janelas.length + " (" + janela.intervalo[0] + " a " + janela.intervalo[1] + " s)";

    // desenha os cartões de todos os canais desta janela
    desenharGrade(janela);

    // desenha a tabela com as potências da janela atual
    desenharPotencias(janela);

}

// começa o programa carrega os exemplos e mostra a primeira janela 
async function iniciar(){
    // primeiro carrega os exeplos 
    await carregar();
    // posicao = 1021;
    // mostra a primeira janela apos carregar 
    mostrar(janelas[0]);
    // mostrar(janelas[posicao]);

    // a cada 3 segundos avanca para a proxima janela | repite a acao em intervalos regulares 
    setInterval(() => {
        // soma 1 na posicao e quando chega ao fim da lista volta para o comeco
        posicao = (posicao + 1) % janelas.length;
        // mostra a janela que esta na nova posicao
        mostrar(janelas[posicao]);
    }, 3000);
}
iniciar();
