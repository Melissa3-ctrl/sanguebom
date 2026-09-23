from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse
import csv
import random
from .models import Doador, Hemocentro, Agendamento, CodigoRecuperacao, Notificacao, Receptor, Campanha
from .emails import enviar_email_agendamento, enviar_email_doacao_realizada

# =========================================================
# PÁGINAS DO SITE
# =========================================================

def home(request):
    return render(request, 'home.html', {
        'lateral_direita': True,
    })
def quero_doar(request):
    return render(request, 'quero_doar.html', {'lateral_direita': True})


def tipos_sanguineos(request):
    return render(request, 'tipos_sanguineos.html', {'lateral_direita': True})


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
            total_agendamentos = Agendamento.objects.filter(doador=doador, status='realizado').count()

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
        'lateral_direita': True,
    })


def duvidas(request):
    return render(request, 'duvidas.html', {'lateral_direita': True})


def locais_para_doar(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('relatorios')
        if hasattr(request.user, 'hemocentro'):
            return redirect('painel_hemocentro')

    hemocentros = Hemocentro.objects.filter(ativo=True).order_by('nome')

    return render(request, 'locais_para_doar.html', {
        'hemocentros': hemocentros,
        'lateral_direita': True,
    })


def campanhas(request):
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

    # Busca as campanhas ativas do banco
    campanhas_lista = Campanha.objects.filter(ativa=True)

    return render(request, 'campanhas.html', {
        'doador': doador,
        'proximo_agendamento': proximo_agendamento,
        'campanhas': campanhas_lista,
        'lateral_direita': True,
    })
# =========================================================
# NOTIFICAÇÕES (DINÂMICAS)
# =========================================================

@login_required(login_url='login')
def notificacoes(request):
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
        'lateral_direita': False,
    })


@login_required(login_url='login')
def marcar_lida(request, id):
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
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

    doador = get_object_or_404(Doador, usuario=request.user)

    agendamentos = Agendamento.objects.filter(
        doador=doador
    ).order_by('data', 'horario')

    total_agendamentos = agendamentos.filter(status='realizado').count()
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
        'lateral_direita': False,
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
    total_receptores = Receptor.objects.filter(ativo=True, status='aprovado').count()

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
        'total_receptores': total_receptores,
        'doacoes_por_mes': list(doacoes_por_mes),
        'tipos': list(tipos),
        'ranking': ranking,
        'proximos': proximos,
        'lateral_direita': False,
    })


# =========================================================
# PAINEL DO HEMOCENTRO (COMPLETO)
# =========================================================

@login_required(login_url='login')
def painel_hemocentro(request):
    try:
        hemocentro = Hemocentro.objects.get(usuario=request.user)
    except Hemocentro.DoesNotExist:
        return redirect('home')

    agendamentos = Agendamento.objects.filter(hemocentro=hemocentro)

    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    tipo_filtro = request.GET.get('tipo', '')
    status_filtro = request.GET.get('status', '')

    if data_inicio:
        agendamentos = agendamentos.filter(data__gte=data_inicio)
    if data_fim:
        agendamentos = agendamentos.filter(data__lte=data_fim)
    if tipo_filtro:
        agendamentos = agendamentos.filter(tipo_doacao=tipo_filtro)
    if status_filtro:
        agendamentos = agendamentos.filter(status=status_filtro)

    agendamentos = agendamentos.order_by('data', 'horario')

    total_agendamentos = agendamentos.count()
    total_doadores = agendamentos.values('doador').distinct().count()
    total_vidas = total_agendamentos * 4

    agendados = agendamentos.filter(status='agendado').count()
    realizados = agendamentos.filter(status='realizado').count()
    cancelados = agendamentos.filter(status='cancelado').count()
    faltaram = agendamentos.filter(status='faltou').count()

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

    tipos_doacao = (
        Agendamento.objects
        .filter(hemocentro=hemocentro)
        .values_list('tipo_doacao', flat=True)
        .distinct()
    )

    return render(request, 'painel_hemocentro.html', {
        'hemocentro': hemocentro,
        'agendamentos': agendamentos,
        'total_agendamentos': total_agendamentos,
        'total_doadores': total_doadores,
        'total_vidas': total_vidas,
        'agendados': agendados,
        'realizados': realizados,
        'cancelados': cancelados,
        'faltaram': faltaram,
        'doacoes_por_mes': list(doacoes_por_mes),
        'tipos': list(tipos),
        'tipos_doacao': tipos_doacao,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_filtro': tipo_filtro,
        'status_filtro': status_filtro,
        'lateral_direita': False,
    })


# =========================================================
# ALTERAR STATUS DO AGENDAMENTO
# =========================================================

@login_required(login_url='login')
def alterar_status(request, id):
    try:
        hemocentro = Hemocentro.objects.get(usuario=request.user)
    except Hemocentro.DoesNotExist:
        return redirect('home')

    agendamento = get_object_or_404(Agendamento, id=id, hemocentro=hemocentro)

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        status_antigo = agendamento.status

        if novo_status in ['agendado', 'realizado', 'cancelado', 'faltou']:
            agendamento.status = novo_status
            agendamento.save()

            doador = agendamento.doador

            # Se tá marcando como REALIZADO
            if novo_status == 'realizado' and status_antigo != 'realizado':

                # Conta só doações realizadas
                total_doacoes = Agendamento.objects.filter(
                    doador=doador,
                    status='realizado'
                ).count()

                # ==========================================
                # 📅 CALCULA PRÓXIMA DOAÇÃO E EXAME
                # ==========================================
                from datetime import timedelta, datetime

                if doador.sexo == 'M':
                    dias_espera = 60
                elif doador.sexo == 'F':
                    dias_espera = 90
                else:
                    dias_espera = 90

                data_base = agendamento.data
                if isinstance(data_base, str):
                    data_base = datetime.strptime(data_base, '%Y-%m-%d').date()

                proxima_doacao = data_base + timedelta(days=dias_espera)
                data_exame = data_base + timedelta(days=9)

                proxima_doacao_fmt = proxima_doacao.strftime('%d/%m/%Y')
                data_exame_fmt = data_exame.strftime('%d/%m/%Y')

                # Define o nível
                if total_doacoes >= 6:
                    nivel = 'Ouro'
                    proximo = None
                    faltam = 0
                    beneficios = '''🎁 Isenção em concursos do DF
🎁 Meia-entrada em eventos culturais
🎁 Prioridade em vacinação
🎁 Selo "Doador Ouro" no perfil
🎁 Certificado digital de doador'''
                elif total_doacoes >= 3:
                    nivel = 'Prata'
                    proximo = 'Ouro'
                    faltam = 6 - total_doacoes
                    beneficios = f'''🎁 Desconto em eventos culturais
🎁 Prioridade em vacinação
🎁 Certificado digital de doador

Faltam apenas {faltam} doações pro nível OURO! 🏆'''
                else:
                    nivel = 'Bronze'
                    proximo = 'Prata'
                    faltam = 3 - total_doacoes
                    beneficios = f'''🎁 Certificado digital de doador
🎁 Acesso ao ranking de doadores

Faltam {faltam} doações pro nível PRATA! 🥈'''

                emoji_nivel = {'Bronze': '🥉', 'Prata': '🥈', 'Ouro': '🥇'}.get(nivel, '')

                # ==========================================
                # 📧 NOTIFICAÇÃO 1: CONFIRMAÇÃO + PROGRESSO
                # ==========================================
                Notificacao.objects.create(
                    doador=doador,
                    tipo='confirmado',
                    titulo=f'✅ Doação confirmada no {hemocentro.nome}!',
                    mensagem=f'''Sua doação foi registrada com sucesso! ❤️

📊 Total de doações: {total_doacoes}
{emoji_nivel} Nível atual: {nivel}
{f'Faltam {faltam} doações pra subir pro {proximo}' if proximo else 'Você atingiu o nível máximo!'}

📅 Próxima doação: {proxima_doacao_fmt}
📋 Exame disponível a partir de: {data_exame_fmt}

Obrigado por salvar vidas! 🩸'''
                )

                # ==========================================
                # 📧 NOTIFICAÇÃO 2: BENEFÍCIOS
                # ==========================================
                Notificacao.objects.create(
                    doador=doador,
                    tipo='nivel',
                    titulo=f'{emoji_nivel} Seus benefícios no nível {nivel}',
                    mensagem=beneficios
                )

                # Envia e-mail de agradecimento
                try:
                    enviar_email_doacao_realizada(doador, agendamento)
                except Exception as e:
                    print(f"Erro ao enviar e-mail de doação realizada: {e}")

            # Se tá marcando outro status (não realizado)
            else:
                Notificacao.objects.create(
                    doador=doador,
                    tipo='lembrete',
                    titulo=f'Status atualizado: {agendamento.get_status_display()}',
                    mensagem=f'Seu agendamento no {hemocentro.nome} para {agendamento.data} foi marcado como {agendamento.get_status_display()}.'
                )

    return redirect('painel_hemocentro')

# =========================================================
# EXPORTAR CSV
# =========================================================

@login_required(login_url='login')
def exportar_csv(request):
    try:
        hemocentro = Hemocentro.objects.get(usuario=request.user)
    except Hemocentro.DoesNotExist:
        return redirect('home')

    agendamentos = Agendamento.objects.filter(hemocentro=hemocentro).order_by('data', 'horario')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="agendamentos_{hemocentro.nome}.csv"'

    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Data', 'Hora', 'Doador', 'Tipo Sanguíneo', 'Telefone', 'Email', 'Tipo Doação', 'Status'])

    for a in agendamentos:
        writer.writerow([
            a.data.strftime('%d/%m/%Y'),
            a.horario.strftime('%H:%M'),
            a.doador.nome,
            a.doador.tipo_sanguineo,
            a.doador.telefone,
            a.doador.email,
            a.tipo_doacao,
            a.get_status_display(),
        ])

    return response


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
            tipo_doacao=tipo_doacao,
            status='agendado'
        )

        Notificacao.objects.create(
            doador=doador,
            tipo='confirmado',
            titulo='✅ Agendamento confirmado',
            mensagem=f'Seu agendamento no {hemocentro.nome} foi confirmado para {data} às {horario}.'
        )

        total = Agendamento.objects.filter(doador=doador, status='realizado').count()
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
        'proximo_agendamento': proximo_agendamento,
        'lateral_direita': False,
    })


# =========================================================
# READ - LISTAR AGENDAMENTOS
# =========================================================

@login_required(login_url='login')
def listar_agendamentos(request):
    if request.user.is_staff:
        return redirect('relatorios')
    if hasattr(request.user, 'hemocentro'):
        return redirect('painel_hemocentro')

    doador = get_object_or_404(Doador, usuario=request.user)

    agendamentos = Agendamento.objects.filter(doador=doador)

    return render(request, 'agendamentos.html', {
        'agendamentos': agendamentos,
        'lateral_direita': False,
    })


# =========================================================
# UPDATE - EDITAR AGENDAMENTO
# =========================================================

@login_required(login_url='login')
def editar_agendamento(request, id):
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
        'hemocentros': hemocentros,
        'lateral_direita': False,
    })


# =========================================================
# DELETE - EXCLUIR AGENDAMENTO
# =========================================================

@login_required(login_url='login')
def excluir_agendamento(request, id):
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
        'agendamento': agendamento,
        'lateral_direita': False,
    })


# =========================================================
# PRECISO DE DOAÇÃO (RECEPTOR)
# =========================================================

def preciso_doacao(request):
    """Página informativa — o formulário vai pro admin/hemocentro."""
    return render(request, 'preciso_doacao.html', {
        'lateral_direita': False,
    })

@login_required(login_url='login')
def cadastrar_receptor(request):
    hemocentros = Hemocentro.objects.filter(ativo=True).order_by('nome')
    cidades = Hemocentro.objects.filter(ativo=True).values_list('cidade', flat=True).distinct().order_by('cidade')

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        idade = request.POST.get('idade_paciente', '').strip()
        sexo = request.POST.get('sexo_paciente', '').strip()
        tipo_sanguineo = request.POST.get('tipo_sanguineo', '')
        tipo_doacao = request.POST.get('tipo_doacao', 'sangue')
        hospital = request.POST.get('hospital', '').strip()
        cidade = request.POST.get('cidade', '').strip()
        urgencia = request.POST.get('urgencia', 'media')
        descricao = request.POST.get('descricao', '').strip()
        email_contato = request.POST.get('email_contato', '').strip()
        celular_contato = request.POST.get('celular_contato', '').strip()
        laudo = request.FILES.get('laudo')

        # Validações
        erros = []
        if not nome:
            erros.append('Nome é obrigatório.')
        if not tipo_sanguineo:
            erros.append('Tipo sanguíneo é obrigatório.')
        if not hospital:
            erros.append('Hospital é obrigatório.')
        if not cidade:
            erros.append('Cidade é obrigatória.')
        if not email_contato and not celular_contato:
            erros.append('Informe pelo menos um contato (e-mail ou celular).')
        if len(descricao) < 20:
            erros.append('Descrição deve ter pelo menos 20 caracteres.')
        if laudo and laudo.size > 5 * 1024 * 1024:
            erros.append('Laudo muito grande. Máximo 5MB.')

        if erros:
            return render(request, 'cadastrar_receptor.html', {
                'erro': ' '.join(erros),
                'hemocentros': hemocentros,
                'cidades': cidades,
            })

        # Monta o campo "contato" unificado
        contato = f"{celular_contato} | {email_contato}"

        # Cria o receptor com TODOS os campos
        receptor = Receptor.objects.create(
            usuario=request.user,
            nome=nome,
            idade_paciente=idade if idade else None,
            sexo_paciente=sexo,
            tipo_sanguineo=tipo_sanguineo,
            tipo_doacao=tipo_doacao,
            hospital=hospital,
            cidade=cidade,
            urgencia=urgencia,
            descricao=descricao,
            email_contato=email_contato,
            celular_contato=celular_contato,
            contato=contato,
            laudo=laudo,
            status='pendente',
            ativo=False
        )

        # Envia e-mail pro admin
        try:
            send_mail(
                subject='🩸 Novo pedido de doação',
                message=f'''Um novo pedido de doação foi cadastrado.

Nome: {nome}
Idade: {idade or 'Não informada'}
Sexo: {sexo or 'Não informado'}
Tipo sanguíneo: {tipo_sanguineo}
Tipo de doação: {tipo_doacao}
Hospital: {hospital}
Cidade: {cidade}
Urgência: {urgencia}
E-mail: {email_contato or 'Não informado'}
Celular: {celular_contato or 'Não informado'}
Laudo anexado: {'Sim' if laudo else 'Não'}

Descrição: {descricao}

Acesse o admin pra aprovar.
''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=True
            )
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

        return render(request, 'cadastrar_receptor.html', {
            'sucesso': 'Pedido enviado com sucesso! O hemocentro entrará em contato.',
            'hemocentros': hemocentros,
            'cidades': cidades,
        })

    return render(request, 'cadastrar_receptor.html', {
        'hemocentros': hemocentros,
        'cidades': cidades,
    })


def detalhes_receptor(request, id):
    receptor = get_object_or_404(Receptor, id=id, status='aprovado', ativo=True)

    receptor.visualizacoes += 1
    receptor.save(update_fields=['visualizacoes'])

    return render(request, 'detalhes_receptor.html', {
        'receptor': receptor,
        'lateral_direita': False,
    })


@login_required(login_url='login')
def quero_ajudar(request, id):
    receptor = get_object_or_404(Receptor, id=id, status='aprovado', ativo=True)

    if receptor.usuario:
        try:
            doador_destino = Doador.objects.get(usuario=receptor.usuario)
            Notificacao.objects.create(
                doador=doador_destino,
                tipo='alerta',
                titulo=f'❤️ Alguém quer ajudar {receptor.nome}!',
                mensagem=f'{request.user.first_name or request.user.username} viu o pedido de {receptor.nome} e quer ajudar.'
            )
        except Doador.DoesNotExist:
            pass

        try:
            if receptor.usuario.email:
                send_mail(
                    subject=f'❤️ Alguém quer ajudar {receptor.nome}!',
                    message=f'''Boa notícia!

{request.user.first_name or request.user.username} viu o pedido de {receptor.nome} e quer ajudar.

Contato de quem quer ajudar: {request.user.email}

Entre em contato!
''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[receptor.usuario.email],
                    fail_silently=True
                )
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

    return redirect('detalhes_receptor', id=receptor.id)


@login_required(login_url='login')
def meus_pedidos(request):
    receptores = Receptor.objects.filter(usuario=request.user).order_by('-criado_em')

    total = receptores.count()
    pendentes = receptores.filter(status='pendente').count()
    aprovados = receptores.filter(status='aprovado').count()
    atendidos = receptores.filter(status='atendido').count()

    return render(request, 'meus_pedidos.html', {
        'receptores': receptores,
        'total': total,
        'pendentes': pendentes,
        'aprovados': aprovados,
        'atendidos': atendidos,
        'lateral_direita': False,
    })


@login_required(login_url='login')
def editar_pedido(request, id):
    receptor = get_object_or_404(Receptor, id=id, usuario=request.user)

    if receptor.status in ['atendido', 'expirado']:
        return redirect('meus_pedidos')

    if request.method == 'POST':
        receptor.nome = request.POST.get('nome', receptor.nome)
        receptor.tipo_sanguineo = request.POST.get('tipo_sanguineo', receptor.tipo_sanguineo)
        receptor.hospital = request.POST.get('hospital', receptor.hospital)
        receptor.cidade = request.POST.get('cidade', receptor.cidade)
        receptor.urgencia = request.POST.get('urgencia', receptor.urgencia)
        receptor.descricao = request.POST.get('descricao', receptor.descricao)
        receptor.contato = request.POST.get('contato', receptor.contato)
        receptor.save()

        return redirect('meus_pedidos')

    return render(request, 'editar_pedido.html', {
        'receptor': receptor,
        'lateral_direita': False,
    })


@login_required(login_url='login')
def excluir_pedido(request, id):
    receptor = get_object_or_404(Receptor, id=id, usuario=request.user)

    if request.method == 'POST':
        receptor.delete()
        return redirect('meus_pedidos')

    return render(request, 'confirmar_exclusao_pedido.html', {
        'receptor': receptor,
        'lateral_direita': False,
    })