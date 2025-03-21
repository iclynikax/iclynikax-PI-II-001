from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from .models import Consulta, Documento
from datetime import datetime


def home(request):
    if request.method == "GET":
        medico_filtrar = request.GET.get('seek_medico')
        especialidades_filtrar = request.GET.getlist('seek_espcldds')

        slct_medicos = DadosMedico.objects.all()
        if medico_filtrar:
            slct_medicos = slct_medicos.filter(nome__icontains = medico_filtrar)

        if especialidades_filtrar:
            slct_medicos = slct_medicos.filter(especialidade_id__in=especialidades_filtrar)        

        slct_espcldds = Especialidades.objects.all()
        return render(request, 'home.html',{'medicos': slct_medicos, 'especialidades':slct_espcldds, 'is_medico': is_medico(request.user)})


def fnctn_esclhr_hrrio(request, id_dados_medicos):
    if request.method == "GET":
        slct_medico = DadosMedico.objects.get(id=id_dados_medicos)
        slct_dts_abertas = DatasAbertas.objects.filter(user=slct_medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
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

        messages.add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')

        return redirect('/pacientes/minhas_consultas/')    

def fnctn_mnhs_cnslts(request):
    if request.method == "GET":
        #TODO: desenvolver filtros
        slct_mnhs_cnslts = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'minhas_consultas.html', {'minhas_consultas': slct_mnhs_cnslts,'is_medico': is_medico(request.user)})


def fnctn_cnslta(request, id_consulta):
    if request.method == 'GET':
        slct_cnslta = Consulta.objects.get(id=id_consulta)
        slct_ddo_mdco = DadosMedico.objects.get(user=slct_cnslta.data_aberta.user)
        slct_dcmnts = Documento.objects.filter(consulta=slct_cnslta)
        return render(request, 'consulta.html', {'consulta': slct_cnslta, 'documentos': slct_dcmnts, 'dado_medico': slct_ddo_mdco, 'is_medico': is_medico(request.user)})


