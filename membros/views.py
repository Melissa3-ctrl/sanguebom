from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
import random

from .models import Doador, Hemocentro, Agendamento, CodigoRecuperacao


# =========================================================
# PÁGINAS DO SITE
# =========================================================

def quero_doar(request):
    return render(request, 'quero_doar.html')


def tipos_sanguineos(request):
    return render(request, 'tipos_sanguineos.html')


def notificacoes(request):
    return render(request, 'notificacoes.html')


def home(request):
    return render(request, 'home.html')


def beneficios(request):
    return render(request, 'beneficios.html')


def campanhas(request):
    return render(request, 'campanhas.html')


def duvidas(request):
    return render(request, 'duvidas.html')


def locais_para_doar(request):
    return render(request, 'locais_para_doar.html')


@login_required(login_url='login')
def meu_perfil(request):
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    return render(request, 'meu_perfil.html', {
        'doador': doador
    })


# =========================================================
# CADASTRO DE DOADOR
# =========================================================

def cadastro(request):

    if request.method == 'POST':

        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        tipo_sanguineo = request.POST.get('tipo_sanguineo')
        data_nascimento = request.POST.get('data_nascimento')
        senha = request.POST.get('senha')

        # Verifica se o e-mail já existe
        if User.objects.filter(username=email).exists():

            return render(request, 'cadastrar.html', {
                'erro': 'Este e-mail já está cadastrado.'
            })

        # Cria o usuário do Django
        usuario = User.objects.create_user(
            username=email,
            email=email,
            password=senha,
            first_name=nome
        )

        # Cria o doador ligado ao usuário
        Doador.objects.create(
            usuario=usuario,
            nome=nome,
            email=email,
            telefone=telefone,
            tipo_sanguineo=tipo_sanguineo,
            data_nascimento=data_nascimento
        )

        # Depois do cadastro, vai para o login
        return redirect('login')

    return render(request, 'cadastrar.html')


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        senha = request.POST.get('senha')

        usuario = authenticate(
            request,
            username=email,
            password=senha
        )

        if usuario is not None:

            login(request, usuario)

            return redirect('agendar_doacao')

        return render(request, 'login.html', {
            'erro': 'E-mail ou senha incorretos.'
        })

    return render(request, 'login.html')


# =========================================================
# RECUPERAR SENHA - ENVIAR CÓDIGO
# =========================================================

def recuperar_senha(request):

    if request.method == 'POST':

        email = request.POST.get('email')

        # Verifica se o e-mail está cadastrado
        usuario = User.objects.filter(
            username=email
        ).first()

        if usuario is None:

            return render(request, 'recuperar_senha.html', {
                'erro': 'Este e-mail não está cadastrado.'
            })

        # Gera um código aleatório de 6 números
        codigo = str(random.randint(100000, 999999))

        # Remove códigos anteriores desse e-mail
        CodigoRecuperacao.objects.filter(
            email=email
        ).delete()

        # Salva o novo código no banco
        CodigoRecuperacao.objects.create(
            email=email,
            codigo=codigo
        )

        # Envia o código para o e-mail
        send_mail(
            'Código para recuperação de senha - Sangue Bom',
            f'Seu código para recuperar a senha é: {codigo}\n\n'
            'Esse código é válido para a recuperação da sua senha.',
            None,
            [email],
            fail_silently=False,
        )

        return render(request, 'recuperar_senha.html', {
            'email': email,
            'codigo_enviado': True,
            'mensagem': 'Um código de recuperação foi enviado para seu e-mail.'
        })

    return render(request, 'recuperar_senha.html')


# =========================================================
# VALIDAR CÓDIGO E ALTERAR SENHA
# =========================================================

def validar_codigo(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        codigo_digitado = request.POST.get('codigo')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # Procura o código salvo
        codigo_recuperacao = CodigoRecuperacao.objects.filter(
            email=email,
            codigo=codigo_digitado
        ).first()

        if codigo_recuperacao is None:

            return render(request, 'recuperar_senha.html', {
                'erro': 'Código inválido ou incorreto.',
                'email': email,
                'codigo_enviado': True
            })

        # Verifica se o código expirou
        tempo_passado = timezone.now() - codigo_recuperacao.criado_em

        if tempo_passado.total_seconds() > 600:

            codigo_recuperacao.delete()

            return render(request, 'recuperar_senha.html', {
                'erro': 'Este código expirou. Solicite um novo código.',
                'email': email
            })

        # Verifica se as senhas são iguais
        if nova_senha != confirmar_senha:

            return render(request, 'recuperar_senha.html', {
                'erro': 'As senhas não são iguais.',
                'email': email,
                'codigo_enviado': True
            })

        # Procura o usuário
        usuario = User.objects.filter(
            username=email
        ).first()

        if usuario is None:

            return render(request, 'recuperar_senha.html', {
                'erro': 'Usuário não encontrado.'
            })

        # Altera a senha
        usuario.set_password(nova_senha)
        usuario.save()

        # Apaga o código depois de usar
        codigo_recuperacao.delete()

        return render(request, 'recuperar_senha.html', {
            'sucesso': 'Senha alterada com sucesso! Você já pode fazer login.'
        })

    return redirect('recuperar_senha')


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect('login')


# =========================================================
# CREATE - AGENDAR DOAÇÃO
# =========================================================

@login_required(login_url='login')
def agendar_doacao(request):

    # Descobre o doador que está logado
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    if request.method == 'POST':

        hemocentro_id = request.POST.get('hemocentro')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        tipo_doacao = request.POST.get('tipo_doacao')

        # Busca o hemocentro escolhido
        hemocentro = get_object_or_404(
            Hemocentro,
            id=hemocentro_id,
            ativo=True
        )

        # Cria o agendamento
        # A base recebe automaticamente o nome
        # do hemocentro escolhido
        Agendamento.objects.create(
            doador=doador,
            hemocentro=hemocentro,
            base=hemocentro.nome,
            data=data,
            horario=horario,
            tipo_doacao=tipo_doacao
        )

        return redirect('listar_agendamentos')

    # Busca somente hemocentros ativos
    hemocentros = Hemocentro.objects.filter(
        ativo=True
    )

    return render(request, 'agendar_doacao.html', {
        'doador': doador,
        'hemocentros': hemocentros
    })


# =========================================================
# READ - LISTAR AGENDAMENTOS
# =========================================================

@login_required(login_url='login')
def listar_agendamentos(request):

    # Descobre o doador logado
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    # Mostra somente os agendamentos desse doador
    agendamentos = Agendamento.objects.filter(
        doador=doador
    )

    return render(request, 'agendamentos.html', {
        'agendamentos': agendamentos
    })


# =========================================================
# UPDATE - EDITAR AGENDAMENTO
# =========================================================

@login_required(login_url='login')
def editar_agendamento(request, id):

    # Descobre o doador logado
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    # Busca somente o agendamento desse doador
    agendamento = get_object_or_404(
        Agendamento,
        id=id,
        doador=doador
    )

    if request.method == 'POST':

        hemocentro_id = request.POST.get('hemocentro')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        tipo_doacao = request.POST.get('tipo_doacao')

        # Busca o novo hemocentro
        hemocentro = get_object_or_404(
            Hemocentro,
            id=hemocentro_id,
            ativo=True
        )

        # Atualiza os dados
        agendamento.hemocentro = hemocentro

        # Atualiza a base automaticamente
        agendamento.base = hemocentro.nome

        agendamento.data = data
        agendamento.horario = horario
        agendamento.tipo_doacao = tipo_doacao

        agendamento.save()

        return redirect('listar_agendamentos')

    # Busca somente hemocentros ativos
    hemocentros = Hemocentro.objects.filter(
        ativo=True
    )

    return render(request, 'editar_agendamento.html', {
        'agendamento': agendamento,
        'hemocentros': hemocentros
    })


# =========================================================
# DELETE - EXCLUIR AGENDAMENTO
# =========================================================

@login_required(login_url='login')
def excluir_agendamento(request, id):

    # Descobre o doador
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    # Busca somente um agendamento
    # que pertence ao usuário logado
    agendamento = get_object_or_404(
        Agendamento,
        id=id,
        doador=doador
    )

    if request.method == 'POST':

        agendamento.delete()

        return redirect('listar_agendamentos')

    return render(request, 'confirmar_exclusao.html', {
        'agendamento': agendamento
    })