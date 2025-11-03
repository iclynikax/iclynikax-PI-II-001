from django.db import models
from django.contrib.auth.models import User
from medico.models import DatasAbertas, DadosMedico
import datetime


from datetime import date


def calcular_idade(dt_nascimento):
    if not dt_nascimento:
        return "Data de nascimento não informada"

    hoje = date.today()
    anos = hoje.year - dt_nascimento.year
    meses = hoje.month - dt_nascimento.month

    # Ajustar caso os meses sejam negativos
    if meses < 0:
        anos -= 1
        meses += 12

    return f"{anos} anos e {meses} meses"


class Pet(models.Model):
    Pet = models.CharField(max_length=50)

    def __str__(self):
        return self.Pet


# ----------------------------------------------------------------------------------------------
# Definindo a Classe de Pet´s do Cliente
class Pet_Cliente(models.Model):
    status_petcliente = (
        ('A', 'Ativo'),
        ('I', 'Inativo')
    )
    cliente = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    Pet = models.ForeignKey(
        Pet, on_delete=models.DO_NOTHING, null=True, blank=True)
    Pet_Raca = models.CharField(max_length=140, null=True, blank=True)
    Pet_Pelagem = models.CharField(max_length=150, null=True, blank=True)
    Pet_Nome = models.CharField(max_length=140, null=True, blank=True)
    Pet_Sexo_Id = (
        ('I', 'Indefindio'),
        ('M', 'Macho'),
        ('F', 'Femea')
    )
    Pet_Sexo = models.CharField(max_length=1, choices=Pet_Sexo_Id, default='I')
    Pet_Foto = models.ImageField(upload_to="fotos_pet", null=True, blank=True)
    status = models.CharField(
        max_length=1, choices=status_petcliente, default='A')
    dt_Nscmnto = models.DateField(null=True, blank=True)  # Data de Nascimento

    def __str__(self):
        return self.cliente.username


class Consulta(models.Model):
    status_choices = (
        ('A', 'Agendada'),
        ('F', 'Finalizada'),
        ('C', 'Cancelada'),
        ('L', 'Avaliada'),
        ('I', 'Iniciada')
    )
    paciente = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    Medico = models.ForeignKey(
        DadosMedico, on_delete=models.DO_NOTHING, null=True, blank=True)
    Pet_Cliente = models.ForeignKey(
        Pet_Cliente, on_delete=models.DO_NOTHING, null=True, blank=True)
    data_aberta = models.ForeignKey(DatasAbertas, on_delete=models.DO_NOTHING)
    status = models.CharField(
        max_length=1, choices=status_choices, default='A')
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.paciente.username


class Documento(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    documento = models.FileField(upload_to='documentos')

    def __str__(self):
        return self.titulo

# -------------------------------------------------------------------------------------------
# Definindo a classe de Notificações, tabela que armazena as notificações geradas


class Notificacao(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(null=True, blank=True)
    NmroWhtsApp = models.CharField(max_length=30, null=True, blank=True)
    token = models.CharField(max_length=150, default='SOME STRING')
    dt_envio = models.DateTimeField(
        default=datetime.datetime.now)  # Data do Envio
    ip_rspsta = models.CharField(max_length=15, default='SOME STRING')
    rspsta_grpo = (
        ('0', 'Não Aprovado'),
        ('2', 'Aprovado'),
        ('3', 'Indefinido')
    )
    rspsta = models.CharField(max_length=1, choices=rspsta_grpo, default='3')
    dt_rspsta = models.DateTimeField(null=True, blank=True)  # Data da Resposta

    def __str__(self):
        return self.NmroWhtsApp
