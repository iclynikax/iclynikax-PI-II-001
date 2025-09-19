from django.db import models
from django.contrib.auth.models import User


def is_Atendente(user):
    return user.groups.filter(name='Atendente').exists()


def is_Cliente(user):
    return user.groups.filter(name='Cliente').exists()


def is_Gerente(user):
    return user.groups.filter(name="Gerente").exists()


def is_Médico(user):
    return user.groups.filter(name='Médico').exists()


def Get_cGrp_Usuario(user):
    Get_cGrp_Usuario = "Desconhecido"
    if (is_Gerente(user)):
        Get_cGrp_Usuario = "Gerente"

    if (is_Atendente(user)):
        Get_cGrp_Usuario = "Atendente"

    if (is_Médico(user)):
        Get_cGrp_Usuario = "Médico"

    if (is_Cliente(user)):
        Get_cGrp_Usuario = "Cliente"

    return Get_cGrp_Usuario


class UfEstados(models.Model):
    UfEstados = models.CharField(max_length=30)

    def __str__(self):
        return self.UfEstados


class Perfil(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    Endereco = models.CharField(max_length=200)
    Bairro = models.CharField(max_length=125)
    Cidade = models.CharField(max_length=175)
    Country = models.CharField(max_length=100, default='Brasil')
    UF = models.ForeignKey(
        UfEstados, on_delete=models.DO_NOTHING, null=True, blank=True)
    CEP = models.CharField(max_length=15)
    Celular = models.CharField(
        max_length=11, blank=True, null=True, verbose_name='Nº telefone celular')
    TelFixo = models.CharField(
        max_length=11, blank=True, null=True, verbose_name='Nº telefone fixo')
    RG = models.ImageField(upload_to="rgs")
    CPF = models.CharField(max_length=14)  # 999.999.999-99 = 14
    Foto = models.ImageField(upload_to="fotos_perfil")
    Descricao = models.TextField(null=True, blank=True)
    Empresa = models.CharField(max_length=200, default='SOME STRING')
    Cargo = models.CharField(max_length=150, default='Indefinido')
    token = models.CharField(max_length=150, default='SOME STRING')

    def __str__(self):
        return self.user.username


class Prfl_Endereco(models.Model):
    status_Prfl_Endereco = (
        ('A', 'Ativo'),
        ('I', 'Inativo')
    ) 
    cliente = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    Endereco = models.CharField(max_length=200)
    Numero = models.CharField(max_length=10, default='0')
    Complemento = models.CharField(max_length=200, blank=True, null=True)
    Bairro = models.CharField(max_length=125)
    Referencia = models.CharField(max_length=175, blank=True, null=True)
    urlGgleMaps = models.URLField(max_length=2000, blank=True, null=True)
    Cidade = models.CharField(max_length=175)
    Country = models.CharField(max_length=100, default='Brasil')
    UF = models.ForeignKey(
        UfEstados, on_delete=models.DO_NOTHING, null=True, blank=True)
    CEP = models.CharField(max_length=9)  # 17700-000
    Descricao = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=1, choices=status_Prfl_Endereco, default='A')

    def __str__(self):
        return self.cliente.username
