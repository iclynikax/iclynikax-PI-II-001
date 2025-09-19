import datetime

def clclar_idade(data_de_nascimento):
    ano_atual = datetime.date.today().year
    ano_nascimento = data_de_nascimento.year
    return ano_atual - ano_nascimento
