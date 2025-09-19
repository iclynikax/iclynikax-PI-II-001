from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . models import Especialidades, DadosMedico, is_medico, DatasAbertas
from paciente.models import Consulta, Documento, Notificacao, Pet_Cliente
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta

@login_required
def fnctn_cdstr_medico(request):

    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já está cadastrado como médico.')
        return redirect('/medicos/abrir_horario')

    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades, 'is_medico': is_medico(request.user)})
    
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')


        #TODO: Validar todos os campos

        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            descricao=descricao,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta,
            user=request.user
        )
        dados_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso.')

        return redirect('/medicos/abrir_horario')

@login_required
def fnctn_open_horario(request):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/logout')

    if request.method == "GET":
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        return render(request, 'open_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    
    elif request.method == "POST":
        data = request.POST.get('data')

        data_formatada = datetime.strptime(data, "%Y-%m-%dT%H:%M")
        
        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING, 'A data deve ser maior ou igual a data atual.')
            return redirect('/medicos/abrir_horario')


        horario_abrir = DatasAbertas(
            data=data,
            user=request.user
        )

        horario_abrir.save()

        messages.add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso.')
        return redirect('/medicos/abrir_horario')
    
def fnctn_cnslts_medico(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/logout')
    
    hoje = datetime.now().date()

    slct_cnslts_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    slct_cnslts_rstnts = Consulta.objects.exclude(id__in=slct_cnslts_hoje.values('id')).filter(data_aberta__user=request.user)

    return render(request, 'consultas_medico.html', {'consultas_hoje': slct_cnslts_rstnts, 'consultas_restantes': slct_cnslts_rstnts, 'is_medico': is_medico(request.user)})



def fnct_cnslta_area_mdco(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/logout')
    

    if request.method == "GET":
        slct_cnslta = Consulta.objects.get(id=id_consulta)
        slct_dcmnts = Documento.objects.filter(consulta=slct_cnslta)
        return render(request, 'consulta_area_medico.html', {'consulta': slct_cnslta, 'documentos': slct_dcmnts, 'is_medico': is_medico(request.user)}) 
    
    elif request.method == "POST":
        # Inicializa a consulta + link da chamada
        slct_cnslta = Consulta.objects.get(id=id_consulta)
        slct_link = request.POST.get('link')

        if slct_cnslta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        elif slct_cnslta.status == "F":
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        slct_cnslta.link = slct_link
        slct_cnslta.status = 'I'
        slct_cnslta.save()

        messages.add_message(request, constants.SUCCESS, 'Consulta inicializada com sucesso.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')    
    


    
def fnct_fnlzar_cnslta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/logout')

    slct_cnslta = Consulta.objects.get(id=id_consulta)

    if request.user != slct_cnslta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não pertence ao usuário logado.')
        return redirect(f'/medicos/abrir_horario/')    


    slct_cnslta.status = 'F'
    slct_cnslta.save()

    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')    



def fnctn_add_notfcacao(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)

    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    titulo = request.POST.get('titulo')
    Nmr_WhtsApp = request.FILES.get('Nmr_WhtsApp')

    if not Nmr_WhtsApp:
        messages.add_message(request, constants.WARNING, 'Adicione o documento.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

    Nmr_WhtsApp = Notificacao(
        consulta    = consulta,
        titulo      = titulo,
        Nmr_WhtsApp = Nmr_WhtsApp

    )

    Notificacao.save()

    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    





def fnctn_add_dcmnto(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    
    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    if not documento:
        messages.add_message(request, constants.WARNING, 'Adicione o documento.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento

    )

    documento.save()

    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


@login_required
def fnct_espclddes_mdca(request):
    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        return render(request, 'especialidades_lista.html', {'especialidades': especialidades, 'is_medico': is_medico(request.user)})


def fnct_espclddes_cdstro(request, id_espcldde):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/logout')
    if request.method == "GET":
        slct_id_espcldde = Especialidades.objects.get(id=id_espcldde)
        return render(request, 'cadastro_especialidade.html', {'especialidade': slct_id_espcldde, 'is_medico': is_medico(request.user)})

    elif request.method == "POST":
        slct_id_espcldde = Especialidades.objects.get(id=id_espcldde)
        get_espcldde = request.POST.get('especialidade')

        slct_id_espcldde.especialidade = get_espcldde
        slct_id_espcldde.save()

        especialidades = Especialidades.objects.all()
        return render(request, 'especialidades_lista.html', {'especialidades': especialidades, 'is_medico': is_medico(request.user)})