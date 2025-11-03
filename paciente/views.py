from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages import constants
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now, make_aware, localtime
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.db.models import Count, DateTimeField


from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico, Exames
from usuarios.models import is_Gerente, is_Atendente, is_Médico, is_Cliente, Get_cGrp_Usuario, Perfil
from usuarios.utilities import clclar_idade
from usuarios.models import Prfl_Endereco
from security.models import Security_Logs
from .models import Consulta, Documento, Notificacao, Pet_Cliente, Pet, calcular_idade
from datetime import datetime, timedelta
from collections import defaultdict

import smtplib
import email.message

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


import time
import uuid
import urllib
import os

# ----------------------------------------------------------------------------------------------------------
# # Acessando a página inicial do sistema


@login_required(login_url='/usuarios/login/')
def home(request):

    Get_IS_GERENTE = is_Gerente(request.user)
    Get_IS_ATENDENTE = is_Atendente(request.user)
    Get_IS_MEDICO = is_Médico(request.user)
    Get_IS_CLIENTE = is_Cliente(request.user)

    if request.method == "GET":
        medico_filtrar = request.GET.get('seek_medico')
        especialidades_filtrar = request.GET.getlist('seek_espcldds')

        slct_medicos = DadosMedico.objects.all()
        dados_medicos = DadosMedico.objects.all()
        if medico_filtrar:
            slct_medicos = slct_medicos.filter(nome__icontains=medico_filtrar)

        if especialidades_filtrar:
            slct_medicos = slct_medicos.filter(
                especialidade_id__in=especialidades_filtrar)

        # Seleção das Atividades por cidades. Usado no Gráfico tipo 'radar'.
        hoje = datetime.now().date()
        mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
        mesAnoCrrnte = f"{mes_extenso} {hoje.year}"
        data_inicio = make_aware(datetime.combine(hoje, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(hoje, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # Filtra pelo período desejado
        dados = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim))
            .values('Cidade', 'Atividade')
            .annotate(total=Count('id'))
        )

        # Cria listas
        atividades = sorted(set(d['Atividade'] for d in dados))
        cidades = sorted(set(d['Cidade'] for d in dados))

        # Calcula o valor máximo de cada atividade
        max_por_atividade = defaultdict(int)
        for d in dados:
            if d['total'] > max_por_atividade[d['Atividade']]:
                max_por_atividade[d['Atividade']] = d['total']

        slct_Cidades = (
            Security_Logs.objects.filter(
                DtHr_Atividade__range=(data_inicio, data_fim))
            # Retorna só os nomes das cidades
            .values_list('Cidade', flat=True)
            .distinct()                        # Remove duplicadas
            # Ordena alfabeticamente
            .order_by('Cidade')
        )
        # Monta estrutura para o gráfico pizza
        sries_dta_Atvddes = []
        for atividade in atividades:
            registro = next(
                (r for r in dados if r['Atividade'] == atividade), None)
            vlres_atvdde = registro['total'] if registro else 0
            sries_dta_Atvddes.append(
                {'atvddeValor': vlres_atvdde * 100, 'atvddeNome': atividade})

        # Monta estrutura para o gráfico radar
        series_data = []
        for cidade in cidades:
            valores = []
            for atividade in atividades:
                registro = next(
                    (r for r in dados if r['Cidade'] == cidade and r['Atividade'] == atividade), None)
                valores.append(registro['total'] if registro else 0)
            series_data.append({'value': valores, 'name': cidade})

        slct_espcldds = Especialidades.objects.all()
        return render(request, 'home.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user),
                                             'IS_GERENTE': Get_IS_GERENTE,
                                             'IS_ATENDENTE': Get_IS_ATENDENTE,
                                             'IS_CLIENTE': Get_IS_CLIENTE,
                                             'IS_MEDICO': Get_IS_MEDICO,
                                             'dados_medicos': dados_medicos,
                                             'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
                                             'medicos': slct_medicos,
                                             'mesAnoCorrente': mesAnoCrrnte,
                                             'Rgstrs_Atvddes': sries_dta_Atvddes,
                                             'Rgstrs_Cddes': slct_Cidades,
                                             'Rgstrs_Series': series_data,
                                             'especialidades': slct_espcldds,
                                             'is_medico': is_medico(request.user)})


def obter_ip_cliente(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]  # Se houver múltiplos IPs, pega o primeiro

    else:
        ip = request.META.get('REMOTE_ADDR')  # IP direto do cliente

    return ip


def fnctn_esclhr_hrrio(request, id_dados_medicos):
    if request.method == "GET":
        slct_medico = DadosMedico.objects.get(id=id_dados_medicos)
        slct_dts_abertas = DatasAbertas.objects.filter(user=slct_medico.user).filter(
            data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico': slct_medico, 'datas_abertas': slct_dts_abertas, 'is_medico': is_medico(request.user)})


def fnctn_agndr_hrrio(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta
        )

        horario_agendado.save()

        # TODO: Sugestão Tornar atomico

        data_aberta.agendado = True
        data_aberta.save()

        messages.add_message(request, constants.SUCCESS,
                             'Horário agendado com sucesso.')

        return redirect('/pacientes/minhas_consultas/')


def fnctn_mnhs_cnslts(request):
    if request.method == "GET":
        # TODO: desenvolver filtros

        # Consultas de hoje
        # slct_mnhs_cnslts = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())

        # Todas as consultas do Clientex
        slct_mnhs_cnslts = Consulta.objects.filter(paciente=request.user)

        return render(request, 'minhas_consultas.html', {'minhas_consultas': slct_mnhs_cnslts, 'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'is_medico': is_medico(request.user)})


def fnctn_cnslta(request, id_consulta):
    if request.method == 'GET':
        # slct_cnslta = Consulta.objects.get(id=id_consulta)
        slct_cnslta = get_object_or_404(Consulta, id=id_consulta)
        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.Medico.user)
        slct_dcmnts = Documento.objects.filter(consulta=id_consulta)
        slct_ntficcoes = Notificacao.objects.filter(consulta=id_consulta)
        slct_id_Perfil = Perfil.objects.get(user=slct_cnslta.paciente)

        slct_Pet_Consulta = Pet_Cliente.objects.get(
            id=slct_cnslta.Pet_Cliente.id)

        # Conta todas as notificações com resposta igual a Indefinido (3).
        slct_TF_add_ntfcacs = Notificacao.objects.filter(
            consulta=id_consulta).filter(rspsta=3).count()

        slct_Pet_Sxos = list(Pet_Cliente.Pet_Sexo_Id)
        slct_Get_Pet = Pet.objects.all().order_by('Pet')

        return render(request, 'consulta.html', {'ntficcoes': slct_ntficcoes,
                                                 'perfil': slct_id_Perfil,
                                                 'lAddNtfccs': slct_TF_add_ntfcacs,
                                                 'consulta': slct_cnslta,
                                                 'cGrp_Usuario': Get_cGrp_Usuario(request.user),
                                                 'Lst_Pets': slct_Get_Pet,
                                                 'Lst_Pts_Sxo': slct_Pet_Sxos,
                                                 'documentos': slct_dcmnts,
                                                 'pet_Consulta': slct_Pet_Consulta,
                                                 'dado_medico': slct_ddo_mdco,
                                                 'is_medico': is_medico(request.user)
                                                 }
                      )


# Lista todas as consultas, de todos os clientes, para que possa atribuir uma notificação de autorização a essa consulta.
def fnctn_atrzacoes(request):
    if request.method == "GET":
        slct_Ntfccoes = Notificacao.objects.all()
        return render(request, 'autorizacoes.html', {'ntficcoes': slct_Ntfccoes, 'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'is_medico': is_medico(request.user)})


# ============================================================================================
# Acessa a Notificação selecionada
# ============================================================================================
@login_required(login_url='/usuarios/login/')
def fnctn_atrzacao(request, id_Ntfccao, id_consulta):
    if request.method == "GET":
        slct_atrza = get_object_or_404(Notificacao, id=id_Ntfccao)

        slct_cnslta = Consulta.objects.get(id=id_consulta)

        slct_Pet_Consulta = Pet_Cliente.objects.get(
            id=slct_cnslta.Pet_Cliente.id)
        slct_Pet_Sxos = list(Pet_Cliente.Pet_Sexo_Id)

        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.Medico.user)
        slct_id_Perfil = Perfil.objects.get(user=slct_cnslta.paciente)
        slct_Get_Pet = Pet.objects.all().order_by('Pet')

        nLenDscrcao = 0
        if slct_atrza.descricao is not None:
            nLenDscrcao = len(slct_atrza.descricao)
        # print(nLenDscrcao)

        if nLenDscrcao == 0:
            cText_Pre = "Autorizo a realização do procedimento cirúrgico "
            cText_Pre += "no animal de nome "
            cText_Pre += slct_Pet_Consulta.Pet_Nome
            cText_Pre += ", espécie "
            cText_Pre += slct_Pet_Consulta.Pet.Pet
            cText_Pre += ", da raça "
            cText_Pre += slct_Pet_Consulta.Pet_Raca
            cText_Pre += ", de sexo "
            cText_Pre += slct_Pet_Consulta.get_Pet_Sexo_display()
            cText_Pre += ", com a idade de "
            cText_Pre += calcular_idade(slct_cnslta.Pet_Cliente.dt_Nscmnto)
            cText_Pre += ", de pelagem "
            cText_Pre += slct_Pet_Consulta.Pet_Pelagem
            cText_Pre += ". Identificação do responsável pelo animal: Nome: "
            cText_Pre += "FILIPE ZAMBAO CPF/CNPJ: --- / RG: --- "
            cText_Pre += "Endereço completo: AV.ANTONIO TIVERON,792 - CENTRO - ADAMANTINA/SP - CEP: 1780000 Telefone/email: (18) 99782-4446, (18) 3521-2422 (Resid)"
            cText_Pre += "Declaro ter sido esclarecido acerca dos possíveis riscos inerentes, durante ou após a realização do procedimento cirúrgico citado, estando "
            cText_Pre += "o referido profissional isento de quaisquer responsabilidades decorrentes de tais riscos. Adamantina, Terça, 25 de Março de 2025. "

            print(cText_Pre)

            slct_atrza.descricao = cText_Pre
            slct_atrza.save()

        parmetros = {
            'atrzacao': slct_atrza,
            'dado_medico': slct_ddo_mdco,
            'consulta': slct_cnslta,
            'perfil': slct_id_Perfil,
            'Lst_Pets': slct_Get_Pet,
            'pet_Consulta': slct_Pet_Consulta,
            'Lst_Pts_Sxo': slct_Pet_Sxos,
            'cGrp_Usuario': Get_cGrp_Usuario(request.user),
            'is_medico': is_medico(request.user),
            'id_Ntfccao': id_Ntfccao,
            'id_consulta': slct_atrza.consulta.id

        }

        return render(request, 'notificacao.html', parmetros)

# =====================================================================================================
# Salva as informações da notificação, sem que seja enviada ao cliente.
# =====================================================================================================


@login_required(login_url='/usuarios/login/')
def fnctn_slvr_ntfccao(request):
    if request.method == "POST":
        id_Consulta = request.POST.get("get_id_Consulta")
        id_Ntfccao = request.POST.get("get_id_Ntfccao")

        slct_atrza = get_object_or_404(Notificacao, id=id_Ntfccao)
        get_titulo = request.POST.get("get_Ntfc_Titulo")
        get_descricao = request.POST.get("get_Ntfc_Dscrcao", "")

        #  salvando no banco
        slct_atrza.titulo = get_titulo
        slct_atrza.descricao = get_descricao

        slct_atrza.save()

        slct_cnslta = Consulta.objects.get(id=id_Consulta)
        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.Medico.user)
        slct_id_Perfil = Perfil.objects.get(user=slct_cnslta.paciente)

        parmetros = {
            'atrzacao': slct_atrza,
            'dado_medico': slct_ddo_mdco,
            'consulta': slct_cnslta,
            'perfil': slct_id_Perfil,
            'cGrp_Usuario': Get_cGrp_Usuario(request.user),
            'is_medico': is_medico(request.user),
            'id_Ntfccao': id_Ntfccao,
            'id_consulta': slct_atrza.consulta.id
        }

        messages.add_message(request, constants.INFO,
                             'Alterações salvas com sucesso...')
        return redirect('url_atrzacao', id_Ntfccao=id_Ntfccao, id_consulta=slct_atrza.consulta.id)

# ================================================================================================================


@login_required(login_url='/usuarios/login/')
def fnctn_atlza_atrzacao(request, id_Ntfccao, id_consulta):
    if request.method == "GET":
        slct_atrza = get_object_or_404(Notificacao, id=id_Ntfccao)
        slct_cnslta = Consulta.objects.get(id=id_consulta)
        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.Medico.user)
        slct_id_Perfil = Perfil.objects.get(user=slct_cnslta.paciente)

        slct_atrza.NmroWhtsApp = "11941847775"
        slct_atrza.save()

        parmetros = {
            'atrzacao': slct_atrza,
            'dado_medico': slct_ddo_mdco,
            'consulta': slct_cnslta,
            'perfil': slct_id_Perfil,
            'cGrp_Usuario': Get_cGrp_Usuario(request.user),
            'is_medico': is_medico(request.user)
        }
        return render(request, 'notificacao.html', parmetros)


# ============================================================================================
# Envia mensagem para o email do cliente.
# ============================================================================================

def gerar_link_email(token):
    url = reverse('url_atrzcao_rspsta', args=[token])
    link_completo = f"http://construplus.net:9090/{url}"
    return link_completo


@login_required(login_url='/usuarios/login/')
def fnctn_envia_email_ntficacao(request, id_Ntfccao):
    if request.method == "GET":
        slct_atrza = get_object_or_404(Notificacao, id=id_Ntfccao)
        slct_cnslta = Consulta.objects.get(id=slct_atrza.consulta.id)
        return redirect('url_atrzacao', id_Ntfccao=id_Ntfccao, id_consulta=slct_atrza.consulta.id)

    elif request.method == "POST":
        slct_atrza = get_object_or_404(Notificacao, id=id_Ntfccao)
        slct_cnslta = Consulta.objects.get(id=slct_atrza.consulta.id)
        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.Medico.user)
        slct_id_Perfil = Perfil.objects.get(user=slct_cnslta.paciente)

        token = uuid.uuid4()  # Gera um token único

        Slct_get_email = slct_cnslta.paciente.email
        user = User.objects.filter(email=Slct_get_email)

        if user.exists():

            usuario = get_object_or_404(user, email=Slct_get_email)

            token = uuid.uuid4()
            slct_atrza.token = token  # Supondo que você tenha um campo 'token' no perfil do usuário
            slct_atrza.dt_envio = datetime.now()
            slct_atrza.save()

            cLink_Aprova = "http://construplus.net:9090/paciente/atrzcao_rspsta/?cToken="
            cLink_Aprova += f"{token}"
            cLink_Aprova += "&nRspsta=2"

            cLink_Desaprova = "http://construplus.net:9090/paciente/atrzcao_rspsta/?cToken="
            cLink_Desaprova += f"{token}"
            cLink_Desaprova += "&nRspsta=0"

            html_links = """
                <a href="
            """

            html_links += cLink_Aprova

            html_links += """
                "' class="btn btn-success btn-dark-color" title="Aprova esta Notifivação">Aprovar</a>
            """

            html_links += """
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="
            """
            html_links += cLink_Desaprova
            html_links += """
                "' class="btn btn-success btn-dark-color" title="Desaprova esta Notifivação">Desaprovar</a>
            """

           # return render(request, 'clientes_lista.html', {'RlcaoDClntes': slct_Clnts_Lsta})

            # cLink += password_reset_confirm
            # cLink += uidb64=uid token=token %}

            # send_mail('Assunto','Esse é o email de teste de enviar email do Django', 'gdmacedo@gmail.com', ['gdmacedo@hotmail.com'])
            # mensagem  = "Corpo da mensagem principal"
            # email = EmailMessage(subject='Assunto do eMail',
            #                    body='Mensagem Principal',
            #                    from_email=settings.EMAIL_HOST_USER,
            #                    to=['gdmacedo@outlook.com']
            #                    )
            # email.send()

            corpo_email = """
            """

            corpo_email += "<html>"
            corpo_email += "<head>"
            corpo_email += "<link href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css' rel='stylesheet' type='text/css' />"
            corpo_email += "<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>"
            corpo_email += "</head>"
            corpo_email += "<body scroll=no>"

            corpo_email += """
            <p>Carissimo 
            """
            corpo_email += usuario.first_name
            corpo_email += """
            , </p>
            """
            corpo_email += """
            """
            corpo_email += slct_atrza.descricao
            corpo_email += """<p>
            <p>Click no link abaixo para aprovar a solicitação acima.</p>
            <p></p>
            <p><b>Link:</b></p>
            """
            corpo_email += """<p><br>"""
            corpo_email += html_links
            corpo_email += """<p>
            <br>
            <p>Projeto Integrador I - Polo Adamantina : 2025</p>
            <p></p>
            <p>UNIVESP - Universidade Virtual de São Paulo</p>
            """
            corpo_email += "</body>"
            corpo_email += "</html>"

            msg = email.message.Message()
            msg['Subject'] = "Aprovação:"
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = Slct_get_email
            password = settings.EMAIL_HOST_PASSWORD
            msg.add_header('Content-Type', 'text/html')
            msg.set_payload(corpo_email)
            s = smtplib.SMTP('smtp.gmail.com: 587')
            s.starttls()
            # Login Credentials for sending the mail
            s.login(msg['From'], password)
            s.sendmail(msg['From'], [msg['To']],
                       msg.as_string().encode('iso-8859-1'))

            messages.add_message(
                request, constants.INFO, 'E-mail de notificação da autorização para aprovação foi enviado com sucesso. Aguardando a aprovação do cliente...')
            return redirect('url_atrzacao', id_Ntfccao=id_Ntfccao, id_consulta=slct_atrza.consulta.id)


@login_required(login_url='/usuarios/login/')
def fnctn_atrzcao_rspsta(request):

    get_cToken = request.GET.get('cToken', 'Não Recebeu o Token')
    get_nRspsta = request.GET.get('nRspsta', 'Não Recebeu')

    slct_atrza = Notificacao.objects.filter(token=get_cToken)
    if slct_atrza.exists():

        slct_atrza = get_object_or_404(Notificacao, token=get_cToken)
        slct_cnslta = Consulta.objects.get(id=slct_atrza.consulta.id)

        if get_nRspsta == 0:
            messages.add_message(request, constants.INFO,
                                 'Esta notificação foi reporovada...'
                                 )

        elif get_nRspsta == 2:
            messages.add_message(request, constants.INFO,
                                 'Esta notificação foi aprovada...'
                                 )

        slct_atrza.ip_rspsta = obter_ip_cliente(request)
        slct_atrza.dt_rspsta = datetime.now()
        slct_atrza.rspsta = get_nRspsta

        slct_atrza.save()

        id_consulta = slct_cnslta.id
        # Gerando a URL dinamicamente
        url = reverse('url_cnslta', args=[id_consulta])
        return redirect(url)

    else:
        messages.add_message(request, constants.INFO, 'URL Invalida')
        return redirect('home')

# ============================================================================================
# Adiciona um novo
# Pets do Cliente.
# ============================================================================================


@login_required(login_url='/usuarios/login/')
def fnctn_pet_clnte_add(request, id_Cliente):
    slct_id_cliente = User.objects.get(id=id_Cliente)
    slct_id_Perfil = Perfil.objects.get(user=slct_id_cliente.id)

    slct_Pet_Sxos = list(Pet_Cliente.Pet_Sexo_Id)
    slct_Get_Pet = Pet.objects.all().order_by('Pet')

    slct_Endrs_Cli = Prfl_Endereco.objects.filter(cliente=slct_id_cliente.id)

    slct_id_Pet_Cli = Pet_Cliente.objects.filter(cliente=slct_id_cliente.id)

    if request.method == "POST":
        obj_Pet = Pet.objects.get(id=request.POST.get('get_Pet_Especie_Add'))
        add_Pet_Pet = obj_Pet
        add_Pet_Pet_Raca = request.POST.get('get_Pet_Raca_Add')
        add_Pet_Pet_Pelagem = request.POST.get('get_Pet_Pelagem_Add')
        add_Pet_Pet_Nome = request.POST.get('get_Pet_Nome_Add')
        add_Pet_Pet_Sexo = request.POST.get('get_Pet_Sexo_Add')

        data_str = request.POST.get('get_Pet_dtNscmnto_Add')
        add_Pet_dtNscmnto = datetime.strptime(
            data_str, "%d/%m/%Y").strftime("%Y-%m-%d")

        newPet = Pet_Cliente.objects.create(
            cliente=slct_id_cliente,
            Pet=add_Pet_Pet,
            Pet_Raca=add_Pet_Pet_Raca,
            Pet_Pelagem=add_Pet_Pet_Pelagem,
            Pet_Nome=add_Pet_Pet_Nome,
            dt_Nscmnto=add_Pet_dtNscmnto,
            Pet_Sexo=add_Pet_Pet_Sexo,
            Pet_Foto="fotos_pet/Pet_Indefinido.jpg"
        )
        newPet.save()

        messages.add_message(
            request, messages.INFO, 'Informaçãoes do Novo Pet do Cliente foram adicionadas com sucesso!!!')

    return render(request, 'cliente.html', {'Lst_Pets': slct_Get_Pet,
                                            'Lst_Pts_Sxo': slct_Pet_Sxos,
                                            'Endrcs_Cli': slct_Endrs_Cli,
                                            'Pets_Cliente': slct_id_Pet_Cli,
                                            'cliente': slct_id_cliente,
                                            'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'perfil': slct_id_Perfil, 'is_medico': is_medico(request.user)})


# ============================================================================================
# Acessa o
# Cadastro dos Pets do Cliente.
# ============================================================================================
@login_required(login_url='/usuarios/login/')
def fnctn_pet_clnte_cdstro(request, id_PetCliente):
    slct_petcliente = get_object_or_404(Pet_Cliente, id=id_PetCliente)
    slct_cliente = User.objects.get(username=slct_petcliente.cliente)

    # nClclo_Idde =  clclar_idade(slct_petcliente.dt_Nscmnto)
    slct_id_Perfil = Perfil.objects.get(user=slct_petcliente.cliente)

    slct_petscliente = Pet_Cliente.objects.filter(cliente=slct_cliente.id)
    slct_PetConsultas = Consulta.objects.filter(Pet_Cliente=id_PetCliente)

    slct_Get_Pet = Pet_Cliente.objects.filter(
        id=id_PetCliente)  # Filtra pelo id fornecido

#    slct_Pet_Sxos = slct_Get_Pet.values_list("Pet_Sexo", flat=True)  # Obtém apenas os valores do campo Pet_Sexo
    slct_Pet_Sxos = list(Pet_Cliente.Pet_Sexo_Id)

    slct_Get_Pet = Pet.objects.all().order_by('Pet')

    nId_Pet = request.POST.get('get_Pet_dtNscmnto')

    if request.method == "GET":
        return render(request, 'pet_cliente.html', {'Lst_Pets': slct_Get_Pet, 'Lst_Pts_Sxo': slct_Pet_Sxos, 'Pet_Cliente': slct_petcliente, 'petConsultas': slct_PetConsultas, 'perfil': slct_id_Perfil, 'Pets_Cliente': slct_petscliente, 'cliente': slct_cliente, 'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'is_medico': is_medico(request.user)})

    elif request.method == "POST":

        data_str = request.POST.get('get_Pet_dtNscmnto')
        get_Pet_dtNscmnto = datetime.strptime(
            data_str, "%d/%m/%Y").strftime("%Y-%m-%d")

        updte_Pet_Clnte = get_object_or_404(Pet_Cliente, id=id_PetCliente)
        updte_Pet_Clnte.Pet_id = request.POST.get('get_Pet_Especie')
        updte_Pet_Clnte.Pet_Raca = request.POST.get('get_Pet_Raca')
        updte_Pet_Clnte.Pet_Pelagem = request.POST.get('get_Pet_Pelagem')
        updte_Pet_Clnte.Pet_Sexo = request.POST.get('get_Pet_Sexo')
        updte_Pet_Clnte.Pet_Nome = request.POST.get('get_Pet_Nome')
        updte_Pet_Clnte.dt_Nscmnto = get_Pet_dtNscmnto

        # updte_Pet_Clnte.  = request.POST.get('get_Pet_Foto')

        updte_Pet_Clnte.save()

        slct_petcliente = get_object_or_404(Pet_Cliente, id=id_PetCliente)

        messages.add_message(
            request, messages.INFO, 'Informaçãoes do Pet do Cliente foram salvas com sucesso!!!')
        return render(request, 'pet_cliente.html', {'Lst_Pets': slct_Get_Pet, 'Lst_Pts_Sxo': slct_Pet_Sxos, 'Pet_Cliente': slct_petcliente, 'petConsultas': slct_PetConsultas, 'perfil': slct_id_Perfil, 'Pets_Cliente': slct_petscliente, 'cliente': slct_cliente, 'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'is_medico': is_medico(request.user)})


# ============================================================================================
# Esta function esta sem acesso ao sitema, pois será implementada no futuro.
# Envia mensagem para o WhatsApp do cliente.
# ============================================================================================
@login_required(login_url='/usuarios/login/')
def fnctn_envia_whtsapp_ntficacao(request, id_Ntfccao):
    if request.method == "GET":
        slct_atrza = get_object_or_404(Notificacao, id=id_Ntfccao)
        slct_cnslta = Consulta.objects.get(id=slct_atrza.consulta.id)
        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.Medico.user)
        slct_id_Perfil = Perfil.objects.get(user=slct_cnslta.paciente)

        token = uuid.uuid4()  # Gera um token único

        # Defina o caminho para o executável do GeckoDriver (Firefox)
        # gecko_driver_path = "/path/to/geckodriver"  # Substitua pelo seu caminho
        # Substitua pelo seu caminho
        gecko_driver_path = "/snap/firefox/6103/usr/bin/geckodriver"

        # Inicialize o driver do Firefox
        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(
            executable_path=gecko_driver_path, options=options)

        # Navegue para o WhatsApp Web
        driver.get("https://web.whatsapp.com/")

        # Aguarde a página carregar e o WhatsApp estar autenticado
        try:
            WebDriverWait(driver, 600).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='_1hE3W']"))
            )
        except:
            print("A página não carregou ou o QR code não foi lido no tempo limite.")
            driver.quit()
            exit(1)

        # Selecione a conversa desejada (use XPath para encontrar o elemento)
        try:
            # Substitua o XPATH pelo elemento que representa a conversa desejada
            conversas = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='_1hE3W']"))
            )
            # Clique na conversa para abrir
            conversas.click()
        except:
            print("Converse não encontrada ou falha ao clicar")
            driver.quit()
            exit(1)

        # Encontre o campo de texto da mensagem
        try:
            campo_mensagem = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='_1jPqQ']"))
            )
            # Insira a mensagem
            campo_mensagem.send_keys(
                "Olá, esta é uma mensagem automatizada via Selenium!")

            # Envie a mensagem
            time.sleep(1)  # Aguarda para o envio
            campo_mensagem.send_keys(Keys.ENTER)
            print("Mensagem enviada com sucesso!")
        except:
            print("Falha ao encontrar o campo de texto ou ao enviar a mensagem.")

        # Aguarde um tempo para manter o navegador aberto (opcional)
        time.sleep(10)

        # Feche o navegador
        driver.quit()

# ============================================================================================
# ============================================================================================


def fnctn_mnhs_atrza(request):
    if request.method == "GET":
        # TODO: desenvolver filtros
        slct_mnhs_atrza = Consulta.objects.filter(
            paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'minhas_autoriza.html', {'minhas_consultas': slct_mnhs_atrza, 'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'is_medico': is_medico(request.user)})


@login_required(login_url='/usuarios/login/')
def fnctn_pcnts_cnsltas(request):
    if request.method == "GET":
        slct_mnhs_atrza = Consulta.objects.all()
        return render(request, 'consultas.html', {'minhas_consultas': slct_mnhs_atrza, 'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'is_medico': is_medico(request.user)})

    elif request.method == "POST":
        slct_mnhs_atrza = Consulta.objects.filter(
            paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'consultas.html', {'minhas_consultas': slct_mnhs_atrza, 'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'is_medico': is_medico(request.user)})


@login_required(login_url='/usuarios/login/')
def fnctn_pcnts_exmes(request):
    if request.method == "GET":
        slct_exames = Exames.objects.all()
        slct_mnhs_atrza = Consulta.objects.filter(
            paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'exames.html', {'Exames': slct_exames, 'minhas_consultas': slct_mnhs_atrza, 'is_medico': is_medico(request.user)})


@login_required(login_url='/usuarios/login/')
def fnctn_pcnts_exme(request, id_exame):
    if request.method == "GET":
        slct_exame = Exames.objects.get(id=id_exame)
        return render(request, 'exame.html', {'Exame': slct_exame})


@login_required(login_url='/usuarios/login/')
def fnctn_add_atrzacao(request, id_consulta):
    if request.method == 'GET':
        slct_cnslta = Consulta.objects.get(id=id_consulta)
        slct_Pet_Cliente = Pet_Cliente.objects.get(
            Pet_Cliente=slct_cnslta.paciente)
        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.Medico.user)
        slct_dcmnts = Documento.objects.filter(consulta=id_consulta)
        slct_ntficcoes = Notificacao.objects.filter(consulta=id_consulta)
        slct_id_Perfil = Perfil.objects.get(user=slct_cnslta.paciente)

        slct_Pet_Sxos = list(Pet_Cliente.Pet_Sexo_Id)

        slct_Get_Pet = Pet.objects.all().order_by('Pet')

        return render(request, 'consulta.html', {'ntficcoes': slct_ntficcoes,
                                                 'perfil': slct_id_Perfil,
                                                 'Lst_Pets': slct_Get_Pet,
                                                 'Lst_Pts_Sxo': slct_Pet_Sxos,
                                                 'Pet_Cliente': slct_Pet_Cliente,
                                                 'consulta': slct_cnslta,
                                                 'cGrp_Usuario': Get_cGrp_Usuario(request.user),
                                                 'documentos': slct_dcmnts,
                                                 'dado_medico': slct_ddo_mdco,
                                                 'is_medico': is_medico(request.user)
                                                 }
                      )

    elif request.method == "POST":
        slct_cnslta = Consulta.objects.get(id=id_consulta)
        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.Medico.user)
        slct_dcmnts = Documento.objects.filter(consulta=id_consulta)
        slct_ntficcoes = Notificacao.objects.filter(consulta=id_consulta)
        slct_id_Perfil = Perfil.objects.get(user=slct_cnslta.paciente)

        Get_NmroCelular = slct_id_Perfil.Celular

        cDescricao = "Autorizo a realização do procedimento "
        cDescricao += "Cirúrgico ......................................................................... no animal de nome FAROFA, espécie Felino, raça SRD (Felino), sexo Fêmea, idade 1 ano e 8 meses, pelagem ---. Identificação do responsável pelo animal: Nome: FILIPE ZAMBAO CPF/CNPJ: --- / RG: --- Endereço completo: AV.ANTONIO TIVERON,792 - CENTRO - ADAMANTINA/SP - CEP: 1780000 Telefone/email: (18) 99782-4446, (18) 3521-2422 (Resid) Declaro ter sido esclarecido acerca dos possíveis riscos inerentes, durante ou após a realização do procedimento cirúrgico citado, estando o referido profissional isento de quaisquer responsabilidades decorrentes de tais riscos. Adamantina, Terça, 25 de Março de 2025. "

        new_NtfKcao = Notificacao(titulo="Termo de autorização para procedimento cirúrgico",
                                  consulta=Consulta.objects.get(
                                      id=id_consulta),
                                  NmroWhtsApp=Get_NmroCelular,
                                  descricao=cDescricao
                                  )
        new_NtfKcao.save()

        return redirect('url_cnslta', id_consulta=slct_cnslta.id)
