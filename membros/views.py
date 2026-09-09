from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Doador, Hemocentro, Agendamento


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

    # Descobre automaticamente qual doador está logado
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    if request.method == 'POST':

        hemocentro_id = request.POST.get('hemocentro')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        tipo_doacao = request.POST.get('tipo_doacao')

        hemocentro = get_object_or_404(
            Hemocentro,
            id=hemocentro_id
        )

        Agendamento.objects.create(
            doador=doador,
            hemocentro=hemocentro,
            data=data,
            horario=horario,
            tipo_doacao=tipo_doacao
        )

        return redirect('listar_agendamentos')

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

    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

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

    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    agendamento = get_object_or_404(
        Agendamento,
        id=id,
        doador=doador
    )

    if request.method == 'POST':

        agendamento.hemocentro_id = request.POST.get(
            'hemocentro'
        )

        agendamento.data = request.POST.get(
            'data'
        )

        agendamento.horario = request.POST.get(
            'horario'
        )

        agendamento.tipo_doacao = request.POST.get(
            'tipo_doacao'
        )

        agendamento.save()

        return redirect('listar_agendamentos')

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

    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

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