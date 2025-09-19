// Verifica se a data digitada esta digitada de forma correta
$(document).ready(function() {
    $("input[name='get_Pet_dtNscmnto']").on("blur", function() {
        var dataDigitada = $(this).val();
        if (!validarFormatoData(dataDigitada)) {
            $("#mensagem").text("Formato inválido! Use DD/MM/YYYY.").css("color", "red");
            $(this).focus(); // Retorna o foco para correção
        } else if (!validarDataNaoFutura(dataDigitada)) {
            $("#mensagem").text("A data não pode ser maior que a data atual!").css("color", "red");
            $(this).focus(); // Retorna o foco para correção
        } else {
            $("#mensagem").text("Data válida!").css("color", "green");
        }
    });
});

function validarFormatoData(data) {
    var regexData = /^\d{2}\/\d{2}\/\d{4}$/; // Formato esperado: DD/MM/YYYY
    return regexData.test(data);
}

function validarDataNaoFutura(data) {
    var partes = data.split("/");
    var dataDigitada = new Date(partes[2], partes[1] - 1, partes[0]); // Ajusta para o formato Date correto
    var dataAtual = new Date();
    
    return dataDigitada <= dataAtual;
}