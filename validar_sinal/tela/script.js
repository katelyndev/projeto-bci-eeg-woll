// mostra as janelas de exemplo uma de cada vez 
// lê o arquivo exemplos_teste_tela.json e atualiza a tela a cada 3 segundos

// arquivo de dados que a tela lê; troque aqui para usar outra fonte
const ARQUIVO_DADOS = "janelas_reais.json"; 

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

// cria a funcao qu vai receber a janela e  abre o bloco todo 
function mostrar(janela){
    // pega o id da pagina e guarda na variavel 
    const quadrado = document.getElementById("quadrado");
    // troca a classe do quadrado pelo estado da janela, trocando "_" por "-"
    // ex.: "sem_decisao" vira "sem-decisao", que é o nome da classe no CSS
    quadrado.className = janela.estado.replace("_", "-");

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
}

// começa o programa carrega os exemplos e mostra a primeira janela 
async function iniciar(){
    // primeiro carrega os exeplos 
    await carregar();

    // mostra a primeira janela apos carregar 
    mostrar(janelas[0]);

    // a cada 3 segundos avanca para a proxima janela | repite a acao em intervalos regulares 
    setInterval(() => {
        // soma 1 na posicao e quando chega ao fim da lista volta para o comeco
        posicao = (posicao + 1) % janelas.length;
        // mostra a janela que esta na nova posicao
        mostrar(janelas[posicao]);
    }, 3000);
}
iniciar();
