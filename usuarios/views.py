from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth

from django.conf import settings

import smtplib
import email.message


def fnct_cdstro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get('confirmar_senha')

        users = User.objects.filter(username=username)

        if users.exists():
            messages.add_message(request, constants.ERROR, 'O Usuário já esta cadastrado...')
            return redirect('/usuarios/cadastro')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'A senhas digitada não são iguais. A Senha e o confirmar senha devem ser iguais...')
            return redirect('/usuarios/cadastro')

        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'A senha deve possuir pelo menos 6 caracteres')
            return redirect('/usuarios/cadastro')
        
        try:
            User.objects.create_user(
                username=username,
                email=email,
                password=senha
            )

            return redirect('/usuarios/login')
        except:
            print('Erro 4')
            return redirect('/usuarios/cadastro')
        

def fnct_login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get("senha")

        user = auth.authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user)
            return redirect('/pacientes/home')

        messages.add_message(request, constants.ERROR, 'Usuário ou senha incorretos')
        return redirect('/usuarios/login')
    

def fnct_resetar(request):
    return render(request, 'rcprrusrnme.html')




def fnct_rcprrusrnme(request):
    if request.method == "GET":
        return render(request, 'rcprrusrnme.html')
    if request.method == "POST":
        get_email = request.POST.get('email')

        user = User.objects.filter(email=get_email)

        if user.exists():
            
            usuario = get_object_or_404(user, email=get_email)

            #send_mail('Assunto','Esse é o email de teste de enviar email do Django', 'gdmacedo@gmail.com', ['gdmacedo@hotmail.com'])
            # mensagem  = "Corpo da mensagem principal"
            # email = EmailMessage(subject='Assunto do eMail',
            #                    body='Mensagem Principal',
            #                    from_email=settings.EMAIL_HOST_USER,
            #                    to=['gdmacedo@outlook.com']
            #                    )
            #email.send()


            corpo_email = """
            <p>Você solicitou seus Username de acesso ao nosso ERP.</p>
            <p><b>Username:</b> 
            """
            corpo_email += usuario.username
            corpo_email += """<p>
            <p>Anote e faça login, para ter o melhor.</p>
            """

            msg = email.message.Message()
            msg['Subject'] = "Recuperando seu nome de acesso [Username]"
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = get_email
            password = settings.EMAIL_HOST_PASSWORD 
            msg.add_header('Content-Type', 'text/html')
            msg.set_payload(corpo_email )

            s = smtplib.SMTP('smtp.gmail.com: 587')
            s.starttls()
            # Login Credentials for sending the mail
            s.login(msg['From'], password)
            s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('iso-8859-1'))


            request.session.flush()
            # TODO: Utilizar messages do Django
            messages.add_message(request, messages.INFO, 'Seu login/Username foi enviado a seu email. Verifica seu email !')
            return redirect('/usuarios/login')

        else:
            messages.add_message(request, messages.ERROR, 'O eMail informado, não se encontra em nosso Cadastro!')
            return render(request, 'rcprrusrnme.html')


def fnct_logout(request):
    auth.logout(request)
    return redirect('/usuarios/login')