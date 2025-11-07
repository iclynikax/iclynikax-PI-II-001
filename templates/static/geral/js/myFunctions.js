//
//
//
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

//================================================================================================================
// A função gerarCategorias(periodo, data) completa e inteligente, 
// que gera categorias de datas para hoje (por hora), mês (por dia) e ano (por mês), com precisão de calendário
//----------------------------------------------------------------------------------------------------------------
function gerarCategorias(periodo, data = new Date()) {
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, '0');
  const dia = String(data.getDate()).padStart(2, '0');

  const categorias = [];

  if (periodo === 'hoje') {
    // 24 horas do dia
    for (let h = 0; h < 25; h++) {
      const hora = String(h).padStart(2, '0');
      categorias.push(`${ano}-${mes}-${dia}T${hora}:00:00.000Z`);
    }
  }
  else if (periodo === 'mes') {
    // Calcula número de dias no mês
    const diasNoMes = new Date(ano, data.getMonth() + 1, 0).getDate();
    for (let d = 1; d <= diasNoMes; d++) {
      const diaMes = String(d).padStart(2, '0');
      categorias.push(`${ano}-${mes}-${diaMes}T00:00:00.000Z`);
    }
  
  }

  else if (periodo === 'ano') {
    // 12 meses do ano
    for (let m = 1; m <= 12; m++) {
      const mesAno = String(m).padStart(2, '0');
      categorias.push(`${ano}-${mesAno}-01T00:00:00.000Z`);
    }
  }

  return categorias;
}
//=================================================================================================================
//Exemplos de uso:                                                    Usado em:
// gerarCategorias('hoje'); // gera 24 horas de hoje                  /security/dashboard.html : renderizarGrafico   
// gerarCategorias('mes');  // gera todos os dias do mês atual
// gerarCategorias('ano');  // gera os 12 meses do ano atual
// Com data personalizada
// gerarCategorias('mes', new Date('2025-11-01'));
//------------------------------------------------------------------------------------------------------------------