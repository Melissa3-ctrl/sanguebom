from django.shortcuts import render


def quero_doar(request):
    return render(request, 'quero_doar.html')


def tipos_sanguineos(request):
    return render(request, 'tipos_sanguineos.html')


def notificacoes(request):
    return render(request, 'notificacoes.html')


def home(request):
    return render(request, 'home.html')


def cadastro(request):
    return render(request, 'cadastro.html')


def beneficios(request):
    return render(request, 'beneficios.html')


def campanhas(request):
    return render(request, 'campanhas.html')


def duvidas(request):
    return render(request, 'duvidas.html')


def locais_para_doar(request):
    return render(request, 'locais_para_doar.html')


def meu_perfil(request):
    return render(request, 'meu_perfil.html')


def agendar_doacao(request):
    return render(request, 'agendar_doacao.html')