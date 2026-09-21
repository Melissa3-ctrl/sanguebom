from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils import timezone
from django.conf import settings
from django.db.models import Count
import random
from .models import Doador, Hemocentro, Agendamento, CodigoRecuperacao, Notificacao
from .emails import enviar_email_agendamento


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
    doador = None
    total_agendamentos = 0
    nivel = 'Bronze'
    progresso = 0
    proximo_nivel = 'Prata'
    faltam = 3

    if request.user.is_authenticated:
        try:
            doador = Doador.objects.get(usuario=request.user)
            total_agendamentos = Agendamento.objects.filter(doador=doador).count()

            if total_agendamentos >= 6:
                nivel = 'Ouro'
                progresso = 100
                proximo_nivel = None
                faltam = 0
            elif total_agendamentos >= 3:
                nivel = 'Prata'
                progresso = int((total_agendamentos / 6) * 100)
                proximo_nivel = 'Ouro'
                faltam = 6 - total_agendamentos
            else:
                nivel = 'Bronze'
                progresso = int((total_agendamentos / 3) * 100)
                proximo_nivel = 'Prata'
                faltam = 3 - total_agendamentos
        except Doador.DoesNotExist:
            pass

    return render(request, 'beneficios.html', {
        'doador': doador,
        'total_agendamentos': total_agendamentos,
        'nivel': nivel,
        'progresso': progresso,
        'proximo_nivel': proximo_nivel,
        'faltam': faltam,
    })


def duvidas(request):
    return render(request, 'duvidas.html')


def locais_para_doar(request):
    # Admin e hemocentro não acessam
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('relatorios')
        if hasattr(request.user, 'hemocentro'):
            return redirect('painel_hemocentro')
    return render(request, 'locais_para_doar.html')


def campanhas(request):
    # Admin e hemocentro não acessam
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('relatorios')
        if hasattr(request.user, 'hemocentro'):
            return redirect('painel_hemocentro')

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


# =========================================================
# NOTIFICAÇÕES (DINÂMICAS)
# =========================================================

@login_required(login_url='login')
def notificacoes(request):
    # Admin e hemocentro não têm notificações
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

    doador = get_object_or_404(Doador, usuario=request.user)

    notificacoes_lista = Notificacao.objects.filter(doador=doador)
    nao_lidas = notificacoes_lista.filter(lida=False).count()

    return render(request, 'notificacoes.html', {
        'notificacoes': notificacoes_lista,
        'nao_lidas': nao_lidas,
    })


@login_required(login_url='login')
def marcar_lida(request, id):
    # Admin e hemocentro não acessam
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

    doador = get_object_or_404(Doador, usuario=request.user)
    notificacao = get_object_or_404(Notificacao, id=id, doador=doador)

    notificacao.lida = True
    notificacao.save()

    return redirect('notificacoes')


@login_required(login_url='login')
def marcar_todas_lidas(request):
    # Admin e hemocentro não acessam
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

    doador = get_object_or_404(Doador, usuario=request.user)
    Notificacao.objects.filter(doador=doador, lida=False).update(lida=True)

    return redirect('notificacoes')


# =========================================================
# MEU PERFIL
# =========================================================

@login_required(login_url='login')
def meu_perfil(request):
    # Admin e hemocentro não acessam
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

    doador = get_object_or_404(Doador, usuario=request.user)

    agendamentos = Agendamento.objects.filter(
        doador=doador
    ).order_by('data', 'horario')

    total_agendamentos = agendamentos.count()
    hoje = timezone.localdate()

    proximo_agendamento = agendamentos.filter(
        data__gte=hoje
    ).order_by('data', 'horario').first()

    if total_agendamentos >= 6:
        nivel = 'Ouro'
        proximo_nivel = None
        faltam = 0
        progresso = 100
    elif total_agendamentos >= 3:
        nivel = 'Prata'
        proximo_nivel = 'Ouro'
        faltam = 6 - total_agendamentos
        progresso = int((total_agendamentos / 6) * 100)
    else:
        nivel = 'Bronze'
        proximo_nivel = 'Prata'
        faltam = 3 - total_agendamentos
        progresso = int((total_agendamentos / 3) * 100)

    return render(request, 'meu_perfil.html', {
        'doador': doador,
        'agendamentos': agendamentos,
        'total_agendamentos': total_agendamentos,
        'vidas_salvas': total_agendamentos * 4,
        'proximo_agendamento': proximo_agendamento,
        'nivel': nivel,
        'proximo_nivel': proximo_nivel,
        'faltam': faltam,
        'progresso': progresso,
    })


# =========================================================
# RELATÓRIOS (ADMIN)
# =========================================================

@login_required(login_url='login')
def relatorios(request):
    if not request.user.is_staff:
        return redirect('home')

    total_doadores = Doador.objects.count()
    total_agendamentos = Agendamento.objects.count()
    total_hemocentros = Hemocentro.objects.count()

    doacoes_por_mes = (
        Agendamento.objects
        .extra(select={'mes': "strftime('%%m', data)"})
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    tipos = (
        Doador.objects
        .values('tipo_sanguineo')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    ranking = (
        Hemocentro.objects
        .annotate(total=Count('agendamento'))
        .order_by('-total')[:5]
    )

    hoje = timezone.localdate()
    proximos = Agendamento.objects.filter(
        data__gte=hoje
    ).order_by('data', 'horario')[:10]

    return render(request, 'relatorios.html', {
        'total_doadores': total_doadores,
        'total_agendamentos': total_agendamentos,
        'total_hemocentros': total_hemocentros,
        'doacoes_por_mes': list(doacoes_por_mes),
        'tipos': list(tipos),
        'ranking': ranking,
        'proximos': proximos,
    })


# =========================================================
# PAINEL DO HEMOCENTRO
# =========================================================

@login_required(login_url='login')
def painel_hemocentro(request):
    try:
        hemocentro = Hemocentro.objects.get(usuario=request.user)
    except Hemocentro.DoesNotExist:
        return redirect('home')

    agendamentos = Agendamento.objects.filter(hemocentro=hemocentro)
    total_agendamentos = agendamentos.count()
    total_doadores = agendamentos.values('doador').distinct().count()

    doacoes_por_mes = (
        agendamentos
        .extra(select={'mes': "strftime('%%m', data)"})
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    tipos = (
        agendamentos
        .values('doador__tipo_sanguineo')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    hoje = timezone.localdate()
    proximos = agendamentos.filter(
        data__gte=hoje
    ).order_by('data', 'horario')[:10]

    return render(request, 'painel_hemocentro.html', {
        'hemocentro': hemocentro,
        'total_agendamentos': total_agendamentos,
        'total_doadores': total_doadores,
        'doacoes_por_mes': list(doacoes_por_mes),
        'tipos': list(tipos),
        'proximos': proximos,
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

    if request.method == 'POST':
        etapa_post = request.POST.get('etapa', '1')

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
        lembrar = request.POST.get('lembrar')

        usuario = authenticate(request, username=email, password=senha)

        if usuario is not None:
            login(request, usuario)

            if lembrar:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)

            if usuario.is_staff:
                return redirect('relatorios')
            elif hasattr(usuario, 'hemocentro'):
                return redirect('painel_hemocentro')
            else:
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
# FUNÇÃO AUXILIAR: E-MAIL DE CÓDIGO BONITO
# =========================================================

def enviar_email_codigo(email, codigo, assunto):
    """Envia e-mail com código de verificação (HTML bonito)"""

    mensagem_texto = f'''Ola!

Seu codigo de verificacao e:

    {codigo}

Este codigo e valido por 10 minutos.

Equipe Sangue Bom ❤️
'''

    mensagem_html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="margin:0; padding:0; font-family:Arial, sans-serif; background:#fcf9f2;">

    <div style="max-width:600px; margin:0 auto; background:white; border-radius:16px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.1);">

        <div style="background:linear-gradient(135deg, #b30000, #7a0000); padding:35px 30px; text-align:center; color:white;">
            <h1 style="margin:0; font-size:28px;">🩸 Sangue Bom</h1>
            <p style="margin:10px 0 0 0; opacity:0.9; font-size:14px;">Recuperacao de senha</p>
        </div>

        <div style="padding:40px 30px;">

            <h2 style="color:#b30000; margin-top:0; font-size:22px;">Ola! 👋</h2>

            <p style="color:#555; font-size:16px; line-height:1.6;">
                Use o codigo abaixo para confirmar sua identidade:
            </p>

            <div style="background:#fcf9f2; border:2px dashed #b30000; border-radius:12px; padding:25px; text-align:center; margin:30px 0;">
                <p style="margin:0; color:#b30000; font-size:13px; letter-spacing:2px; text-transform:uppercase;">Seu codigo</p>
                <p style="margin:10px 0 0 0; color:#b30000; font-size:42px; font-weight:bold; letter-spacing:8px; font-family:'Courier New', monospace;">{codigo}</p>
            </div>

            <p style="color:#888; font-size:14px; text-align:center;">
                ⏱️ Este codigo e valido por <strong>10 minutos</strong>
            </p>

            <div style="background:#fff3cd; border-left:4px solid #ffc107; padding:15px; border-radius:8px; margin-top:25px;">
                <p style="margin:0; color:#856404; font-size:13px;">
                    ⚠️ <strong>Importante:</strong> Se voce nao solicitou, ignore este e-mail.
                </p>
            </div>

        </div>

        <div style="background:#7a0000; color:rgba(255,255,255,0.8); padding:20px; text-align:center; font-size:13px;">
            <p style="margin:5px 0;">Doe sangue. Doe vida. 🩸</p>
            <p style="margin:10px 0 0 0; opacity:0.7;">Equipe Sangue Bom ❤️</p>
        </div>

    </div>

</body>
</html>
'''

    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=mensagem_texto,
        from_email=settings.EMAIL_HOST_USER,
        to=[email]
    )
    email_msg.attach_alternative(mensagem_html, "text/html")
    email_msg.send(fail_silently=False)


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

        enviar_email_codigo(
            email,
            codigo,
            '🩸 Seu código de verificação - Sangue Bom'
        )

        return render(request, 'recuperar_senha.html', {
            'email': email,
            'codigo_enviado': True,
            'mensagem': 'Um código de verificação foi enviado para seu e-mail. Verifique também a caixa de spam.'
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
# REENVIAR CÓDIGO
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

        ultimo_codigo = CodigoRecuperacao.objects.filter(email=email).first()

        if ultimo_codigo:
            tempo_passado = timezone.now() - ultimo_codigo.criado_em
            segundos_passados = tempo_passado.total_seconds()

            if segundos_passados < 60:
                segundos_restantes = int(60 - segundos_passados)
                return render(request, 'recuperar_senha.html', {
                    'erro': f'⏱️ Aguarde {segundos_restantes} segundos para reenviar.',
                    'email': email,
                    'codigo_enviado': True
                })

        codigo = str(random.randint(100000, 999999))

        CodigoRecuperacao.objects.filter(email=email).delete()
        CodigoRecuperacao.objects.create(email=email, codigo=codigo)

        enviar_email_codigo(
            email,
            codigo,
            '🔄 Novo código de verificação - Sangue Bom'
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

        if len(nova_senha) < 8:
            return render(request, 'recuperar_senha.html', {
                'erro': 'A senha deve ter pelo menos 8 caracteres.',
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
    # Admin e hemocentro não acessam
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

    doador = get_object_or_404(Doador, usuario=request.user)

    if request.method == 'POST':
        hemocentro_id = request.POST.get('hemocentro')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        tipo_doacao = request.POST.get('tipo_doacao')

        hemocentro = get_object_or_404(Hemocentro, id=hemocentro_id, ativo=True)

        agendamento = Agendamento.objects.create(
            doador=doador,
            hemocentro=hemocentro,
            base=hemocentro.nome,
            data=data,
            horario=horario,
            tipo_doacao=tipo_doacao
        )

        Notificacao.objects.create(
            doador=doador,
            tipo='confirmado',
            titulo='✅ Agendamento confirmado',
            mensagem=f'Seu agendamento no {hemocentro.nome} foi confirmado para {data} às {horario}.'
        )

        total = Agendamento.objects.filter(doador=doador).count()

        if total >= 6:
            Notificacao.objects.create(
                doador=doador,
                tipo='nivel',
                titulo='🏆 Você atingiu o nível Ouro!',
                mensagem='Parabéns! Você desbloqueou todos os benefícios.'
            )
        elif total >= 3:
            Notificacao.objects.create(
                doador=doador,
                tipo='nivel',
                titulo='🥈 Você subiu pro nível Prata!',
                mensagem=f'Faltam {6 - total} agendamentos pro Ouro.'
            )
        else:
            Notificacao.objects.create(
                doador=doador,
                tipo='nivel',
                titulo='🥉 Nível Bronze',
                mensagem=f'Faltam {3 - total} agendamentos pro Prata!'
            )

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
    # Admin e hemocentro não acessam
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

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
    # Admin e hemocentro não acessam
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

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
    # Admin e hemocentro não acessam
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

    doador = get_object_or_404(Doador, usuario=request.user)
    agendamento = get_object_or_404(Agendamento, id=id, doador=doador)

    if request.method == 'POST':
        agendamento.delete()
        return redirect('listar_agendamentos')

    return render(request, 'confirmar_exclusao.html', {
        'agendamento': agendamento
    })