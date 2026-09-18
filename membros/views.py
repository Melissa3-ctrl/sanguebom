from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
import random
from .models import Doador, Hemocentro, Agendamento, CodigoRecuperacao
from .emails import enviar_email_agendamento    # 👈 NOVO IMPORT


# =========================================================
# PÁGINAS DO SITE
# =========================================================

def home(request):
    return render(request, 'home.html')


def quero_doar(request):
    return render(request, 'quero_doar.html')


def tipos_sanguineos(request):
    return render(request, 'tipos_sanguineos.html')


def beneficios(request):
    return render(request, 'beneficios.html')


def duvidas(request):
    return render(request, 'duvidas.html')


def locais_para_doar(request):
    return render(request, 'locais_para_doar.html')


def campanhas(request):
    if not request.user.is_authenticated:
        return redirect('login')

    doador = get_object_or_404(Doador, usuario=request.user)
    hoje = timezone.localdate()

    proximo_agendamento = Agendamento.objects.filter(
        doador=doador,
        data__gte=hoje
    ).order_by('data', 'horario').first()

    return render(request, 'campanhas.html', {
        'doador': doador,
        'proximo_agendamento': proximo_agendamento,
    })


def notificacoes(request):
    if not request.user.is_authenticated:
        return redirect('login')

    doador = get_object_or_404(Doador, usuario=request.user)

    agendamento = Agendamento.objects.filter(
        doador=doador
    ).order_by('-data', '-horario').first()

    agendamento_confirmado = None
    if agendamento:
        agendamento_confirmado = (
            f"Seu agendamento para doação no "
            f"{agendamento.hemocentro.nome} foi confirmado para "
            f"{agendamento.data.strftime('%d/%m/%Y')} às "
            f"{agendamento.horario.strftime('%H:%M')}."
        )

    return render(request, 'notificacoes.html', {
        'alerta_estoque': None,
        'lembrete_doacao': None,
        'campanha': None,
        'agendamento_confirmado': agendamento_confirmado,
    })


@login_required(login_url='login')
def meu_perfil(request):
    doador = get_object_or_404(Doador, usuario=request.user)

    agendamentos = Agendamento.objects.filter(
        doador=doador
    ).order_by('data', 'horario')

    total_agendamentos = agendamentos.count()
    hoje = timezone.localdate()

    proximo_agendamento = agendamentos.filter(
        data__gte=hoje
    ).order_by('data', 'horario').first()

    return render(request, 'meu_perfil.html', {
        'doador': doador,
        'agendamentos': agendamentos,
        'total_agendamentos': total_agendamentos,
        'proximo_agendamento': proximo_agendamento,
    })


# =========================================================
# CADASTRO DE DOADOR - 3 ETAPAS
# =========================================================

def cadastro(request):
    dados = request.session.get('cadastro_dados', {})
    etapa = request.GET.get('etapa', '1')

    estados = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
        ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]

    cidades_por_estado = {
        'DF': ['Brasília'],
        'GO': [
            'Águas Lindas de Goiás', 'Anápolis',
            'Aparecida de Goiânia', 'Catalão', 'Formosa',
            'Goiânia', 'Luziânia', 'Planaltina', 'Valparaíso de Goiás'
        ],
        'MG': ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora'],
        'SP': ['São Paulo', 'Campinas', 'Santos', 'Guarulhos'],
        'RJ': ['Rio de Janeiro', 'Niterói', 'Duque de Caxias'],
    }

    cidades = cidades_por_estado.get(dados.get('estado'), [])

    # =====================================================
    # POST
    # =====================================================
    if request.method == 'POST':
        etapa_post = request.POST.get('etapa', '1')

        # ---------- ETAPA 1 ----------
        if etapa_post == '1':
            dados['nome'] = request.POST.get('nome', '')
            dados['email'] = request.POST.get('email', '')
            dados['cpf'] = request.POST.get('cpf', '')
            dados['data_nascimento'] = request.POST.get('data_nascimento', '')
            dados['sexo'] = request.POST.get('sexo', '')
            dados['tipo_sanguineo'] = request.POST.get('tipo_sanguineo', '')

            if User.objects.filter(username=dados['email']).exists():
                return render(request, 'cadastrar.html', {
                    'etapa': '1',
                    'dados': dados,
                    'erro': 'Este e-mail já está cadastrado.'
                })

            request.session['cadastro_dados'] = dados
            return redirect('/cadastro/?etapa=2')

        # ---------- ETAPA 2 ----------
        elif etapa_post == '2':
            dados['telefone'] = request.POST.get('telefone', '')
            dados['estado'] = request.POST.get('estado', '')
            dados['cidade'] = request.POST.get('cidade', '')

            request.session['cadastro_dados'] = dados

            cidades = cidades_por_estado.get(dados.get('estado'), [])
            acao = request.POST.get('acao')

            if acao == 'ver_cidades':
                return render(request, 'cadastrar.html', {
                    'etapa': '2',
                    'dados': dados,
                    'estados': estados,
                    'cidades': cidades
                })

            if acao == 'continuar':
                if not dados.get('cidade'):
                    return render(request, 'cadastrar.html', {
                        'etapa': '2',
                        'dados': dados,
                        'estados': estados,
                        'cidades': cidades,
                        'erro': 'Selecione uma cidade.'
                    })
                return redirect('/cadastro/?etapa=3')

        # ---------- ETAPA 3 ----------
        elif etapa_post == '3':
            senha = request.POST.get('senha', '')
            confirmar_senha = request.POST.get('confirmar_senha', '')

            if senha != confirmar_senha:
                return render(request, 'cadastrar.html', {
                    'etapa': '3',
                    'dados': dados,
                    'erro': 'As senhas não são iguais.'
                })

            if len(senha) < 8:
                return render(request, 'cadastrar.html', {
                    'etapa': '3',
                    'dados': dados,
                    'erro': 'A senha deve ter pelo menos 8 caracteres.'
                })

            if User.objects.filter(username=dados.get('email')).exists():
                return render(request, 'cadastrar.html', {
                    'etapa': '3',
                    'dados': dados,
                    'erro': 'Este e-mail já está cadastrado.'
                })

            usuario = User.objects.create_user(
                username=dados['email'],
                email=dados['email'],
                password=senha,
                first_name=dados['nome']
            )

            Doador.objects.create(
                usuario=usuario,
                nome=dados['nome'],
                email=dados['email'],
                telefone=dados.get('telefone', ''),
                tipo_sanguineo=dados.get('tipo_sanguineo', ''),
                data_nascimento=dados['data_nascimento']
            )

            request.session.pop('cadastro_dados', None)
            return redirect('login')

    # =====================================================
    # GET
    # =====================================================
    return render(request, 'cadastrar.html', {
        'etapa': etapa,
        'dados': dados,
        'estados': estados,
        'cidades': cidades
    })


# =========================================================
# LOGIN
# =========================================================

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        usuario = authenticate(request, username=email, password=senha)

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
# RECUPERAR SENHA - ENVIAR CÓDIGO
# =========================================================

def recuperar_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        usuario = User.objects.filter(username=email).first()

        if usuario is None:
            return render(request, 'recuperar_senha.html', {
                'erro': 'Este e-mail não está cadastrado.'
            })

        codigo = str(random.randint(100000, 999999))

        CodigoRecuperacao.objects.filter(email=email).delete()
        CodigoRecuperacao.objects.create(email=email, codigo=codigo)

        send_mail(
            'Código de verificação - Sangue Bom',
            f'''Olá!

Recebemos uma solicitação para recuperação de senha da sua conta no Sangue Bom.

Seu código de verificação é:

{codigo}

Digite esse código na página de recuperação de senha para confirmar sua solicitação.

Importante: este código é válido por 10 minutos.

Atenciosamente,
Equipe Sangue Bom ❤️
''',
            None,
            [email],
            fail_silently=False,
        )

        return render(request, 'recuperar_senha.html', {
            'email': email,
            'codigo_enviado': True,
            'mensagem': 'Um código de verificação foi enviado para seu e-mail.'
        })

    return render(request, 'recuperar_senha.html')


# =========================================================
# VALIDAR CÓDIGO
# =========================================================

def validar_codigo(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        codigo_digitado = request.POST.get('codigo')

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

        tempo_passado = timezone.now() - codigo_recuperacao.criado_em

        if tempo_passado.total_seconds() > 600:
            codigo_recuperacao.delete()
            return render(request, 'recuperar_senha.html', {
                'erro': 'Este código expirou. Solicite um novo código.',
                'email': email
            })

        return render(request, 'recuperar_senha.html', {
            'email': email,
            'codigo': codigo_digitado,
            'codigo_validado': True,
            'mensagem': 'Código confirmado com sucesso!'
        })

    return redirect('recuperar_senha')


# =========================================================
# REENVIAR CÓDIGO (NOVO)
# =========================================================

def reenviar_codigo(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        usuario = User.objects.filter(username=email).first()

        if usuario is None:
            return render(request, 'recuperar_senha.html', {
                'erro': 'E-mail não encontrado.',
                'email': email
            })

        # Verifica o último código criado
        ultimo_codigo = CodigoRecuperacao.objects.filter(email=email).first()

        if ultimo_codigo:
            tempo_passado = timezone.now() - ultimo_codigo.criado_em
            segundos_passados = tempo_passado.total_seconds()

            # ⏱️ Só pode reenviar depois de 60 segundos
            if segundos_passados < 60:
                segundos_restantes = int(60 - segundos_passados)
                return render(request, 'recuperar_senha.html', {
                    'erro': f'⏱️ Aguarde {segundos_restantes} segundos para reenviar.',
                    'email': email,
                    'codigo_enviado': True
                })

        # Gera novo código
        codigo = str(random.randint(100000, 999999))

        CodigoRecuperacao.objects.filter(email=email).delete()
        CodigoRecuperacao.objects.create(email=email, codigo=codigo)

        send_mail(
            'Novo código de verificação - Sangue Bom',
            f'''Olá!

Você solicitou um novo código de verificação.

Seu novo código é:

{codigo}

Este código é válido por 10 minutos.

Equipe Sangue Bom ❤️
''',
            None,
            [email],
            fail_silently=False,
        )

        return render(request, 'recuperar_senha.html', {
            'email': email,
            'codigo_enviado': True,
            'mensagem': '🔄 Um novo código foi enviado para seu e-mail.'
        })

    return redirect('recuperar_senha')


# =========================================================
# ALTERAR SENHA
# =========================================================

def alterar_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        codigo = request.POST.get('codigo')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        codigo_recuperacao = CodigoRecuperacao.objects.filter(
            email=email,
            codigo=codigo
        ).first()

        if codigo_recuperacao is None:
            return render(request, 'recuperar_senha.html', {
                'erro': 'Código inválido ou incorreto.',
                'email': email,
                'codigo_enviado': True
            })

        tempo_passado = timezone.now() - codigo_recuperacao.criado_em

        if tempo_passado.total_seconds() > 600:
            codigo_recuperacao.delete()
            return render(request, 'recuperar_senha.html', {
                'erro': 'Este código expirou. Solicite um novo código.',
                'email': email
            })

        if nova_senha != confirmar_senha:
            return render(request, 'recuperar_senha.html', {
                'erro': 'As senhas não são iguais.',
                'email': email,
                'codigo': codigo,
                'codigo_validado': True
            })

        usuario = User.objects.filter(username=email).first()

        if usuario is None:
            return render(request, 'recuperar_senha.html', {
                'erro': 'Usuário não encontrado.',
                'email': email,
                'codigo': codigo,
                'codigo_validado': True
            })

        usuario.set_password(nova_senha)
        usuario.save()

        codigo_recuperacao.delete()

        return render(request, 'recuperar_senha.html', {
            'sucesso': 'Senha alterada com sucesso! Você já pode fazer login.'
        })

    return redirect('recuperar_senha')


# =========================================================
# CREATE - AGENDAR DOAÇÃO
# =========================================================

@login_required(login_url='login')
def agendar_doacao(request):
    doador = get_object_or_404(Doador, usuario=request.user)

    if request.method == 'POST':
        hemocentro_id = request.POST.get('hemocentro')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        tipo_doacao = request.POST.get('tipo_doacao')

        hemocentro = get_object_or_404(Hemocentro, id=hemocentro_id, ativo=True)

        # Salva em variável pra poder enviar email
        agendamento = Agendamento.objects.create(
            doador=doador,
            hemocentro=hemocentro,
            base=hemocentro.nome,
            data=data,
            horario=horario,
            tipo_doacao=tipo_doacao
        )

        # 🎯 ENVIA E-MAIL (doador + hemocentro)
        try:
            enviar_email_agendamento(doador, agendamento)
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

        return redirect('listar_agendamentos')

    hemocentros = Hemocentro.objects.filter(ativo=True)
    hoje = timezone.localdate()

    proximo_agendamento = Agendamento.objects.filter(
        doador=doador,
        data__gte=hoje
    ).order_by('data', 'horario').first()

    return render(request, 'agendar_doacao.html', {
        'doador': doador,
        'hemocentros': hemocentros,
        'proximo_agendamento': proximo_agendamento
    })


# =========================================================
# READ - LISTAR AGENDAMENTOS
# =========================================================

@login_required(login_url='login')
def listar_agendamentos(request):
    doador = get_object_or_404(Doador, usuario=request.user)

    agendamentos = Agendamento.objects.filter(doador=doador)

    return render(request, 'agendamentos.html', {
        'agendamentos': agendamentos
    })


# =========================================================
# UPDATE - EDITAR AGENDAMENTO
# =========================================================

@login_required(login_url='login')
def editar_agendamento(request, id):
    doador = get_object_or_404(Doador, usuario=request.user)
    agendamento = get_object_or_404(Agendamento, id=id, doador=doador)

    if request.method == 'POST':
        hemocentro_id = request.POST.get('hemocentro')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        tipo_doacao = request.POST.get('tipo_doacao')

        hemocentro = get_object_or_404(Hemocentro, id=hemocentro_id, ativo=True)

        agendamento.hemocentro = hemocentro
        agendamento.base = hemocentro.nome
        agendamento.data = data
        agendamento.horario = horario
        agendamento.tipo_doacao = tipo_doacao
        agendamento.save()

        # 🎯 ENVIA E-MAIL DE ATUALIZAÇÃO
        try:
            enviar_email_agendamento(doador, agendamento)
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

        return redirect('listar_agendamentos')

    hemocentros = Hemocentro.objects.filter(ativo=True)

    return render(request, 'editar_agendamento.html', {
        'agendamento': agendamento,
        'hemocentros': hemocentros
    })


# =========================================================
# DELETE - EXCLUIR AGENDAMENTO
# =========================================================

@login_required(login_url='login')
def excluir_agendamento(request, id):
    doador = get_object_or_404(Doador, usuario=request.user)
    agendamento = get_object_or_404(Agendamento, id=id, doador=doador)

    if request.method == 'POST':
        agendamento.delete()
        return redirect('listar_agendamentos')

    return render(request, 'confirmar_exclusao.html', {
        'agendamento': agendamento
    })