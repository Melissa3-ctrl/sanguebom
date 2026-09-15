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

    # Verifica se o usuário está logado
    if not request.user.is_authenticated:
        return redirect('login')

    # Descobre o doador que está logado
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    # Busca o agendamento mais recente desse doador
    agendamento = Agendamento.objects.filter(
        doador=doador
    ).order_by(
        '-data',
        '-horario'
    ).first()

    # Mensagem do agendamento
    agendamento_confirmado = None

    if agendamento:
        agendamento_confirmado = (
            f"Seu agendamento para doação no "
            f"{agendamento.hemocentro.nome} foi confirmado para "
            f"{agendamento.data.strftime('%d/%m/%Y')} às "
            f"{agendamento.horario.strftime('%H:%M')}."
        )

    # Outras notificações
    alerta_estoque = None
    lembrete_doacao = None
    campanha = None

    return render(request, 'notificacoes.html', {
        'alerta_estoque': alerta_estoque,
        'lembrete_doacao': lembrete_doacao,
        'campanha': campanha,
        'agendamento_confirmado': agendamento_confirmado,
    })


def home(request):
    return render(request, 'home.html')


def beneficios(request):
    return render(request, 'beneficios.html')


def campanhas(request):

    # Verifica se o usuário está logado
    if not request.user.is_authenticated:
        return redirect('login')

    # Descobre o doador que está logado
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    # Data atual
    hoje = timezone.localdate()

    # Busca o próximo agendamento desse doador
    proximo_agendamento = Agendamento.objects.filter(
        doador=doador,
        data__gte=hoje
    ).order_by(
        'data',
        'horario'
    ).first()

    return render(request, 'campanhas.html', {
        'doador': doador,
        'proximo_agendamento': proximo_agendamento,
    })


def duvidas(request):
    return render(request, 'duvidas.html')


def locais_para_doar(request):
    return render(request, 'locais_para_doar.html')


@login_required(login_url='login')
def meu_perfil(request):

    # Descobre o doador que está logado
    doador = get_object_or_404(
        Doador,
        usuario=request.user
    )

    # Busca todos os agendamentos desse doador
    agendamentos = Agendamento.objects.filter(
        doador=doador
    ).order_by(
        'data',
        'horario'
    )

    # Quantidade total de agendamentos
    total_agendamentos = agendamentos.count()

    # Data atual
    hoje = timezone.localdate()

    # Busca o próximo agendamento
    proximo_agendamento = agendamentos.filter(
        data__gte=hoje
    ).order_by(
        'data',
        'horario'
    ).first()

    return render(request, 'meu_perfil.html', {
        # Dados do usuário
        'doador': doador,

        # Agendamentos do usuário
        'agendamentos': agendamentos,

        # Total de agendamentos
        'total_agendamentos': total_agendamentos,

        # Próximo agendamento
        'proximo_agendamento': proximo_agendamento,
    })


# =========================================================
# CADASTRO DE DOADOR - 3 ETAPAS
# =========================================================

def cadastro(request):

    # Recupera os dados temporários da sessão
    dados = request.session.get('cadastro_dados', {})

    # Define a etapa atual
    etapa = request.GET.get('etapa', '1')

    # =====================================================
    # POST
    # =====================================================

    if request.method == 'POST':

        etapa_post = request.POST.get('etapa', '1')

        # =================================================
        # ETAPA 1 - DADOS PESSOAIS
        # =================================================

        if etapa_post == '1':

            dados['nome'] = request.POST.get('nome', '')
            dados['email'] = request.POST.get('email', '')
            dados['cpf'] = request.POST.get('cpf', '')
            dados['data_nascimento'] = request.POST.get(
                'data_nascimento',
                ''
            )
            dados['sexo'] = request.POST.get('sexo', '')
            dados['tipo_sanguineo'] = request.POST.get(
                'tipo_sanguineo',
                ''
            )

            # Verifica se o e-mail já existe
            if User.objects.filter(
                username=dados['email']
            ).exists():

                return render(request, 'cadastrar.html', {
                    'etapa': '1',
                    'dados': dados,
                    'erro': 'Este e-mail já está cadastrado.'
                })

            # Salva os dados na sessão
            request.session['cadastro_dados'] = dados

            # Vai para a etapa 2
            return redirect('/cadastro/?etapa=2')


        # =================================================
        # ETAPA 2 - CONTATO E LOCALIZAÇÃO
        # =================================================

        elif etapa_post == '2':

            dados['telefone'] = request.POST.get(
                'telefone',
                ''
            )

            dados['estado'] = request.POST.get(
                'estado',
                ''
            )

            dados['cidade'] = request.POST.get(
                'cidade',
                ''
            )

            # Salva os dados
            request.session['cadastro_dados'] = dados

            # Lista de estados
            estados = [
                ('AC', 'Acre'),
                ('AL', 'Alagoas'),
                ('AP', 'Amapá'),
                ('AM', 'Amazonas'),
                ('BA', 'Bahia'),
                ('CE', 'Ceará'),
                ('DF', 'Distrito Federal'),
                ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'),
                ('MA', 'Maranhão'),
                ('MT', 'Mato Grosso'),
                ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'),
                ('PA', 'Pará'),
                ('PB', 'Paraíba'),
                ('PR', 'Paraná'),
                ('PE', 'Pernambuco'),
                ('PI', 'Piauí'),
                ('RJ', 'Rio de Janeiro'),
                ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'),
                ('RO', 'Rondônia'),
                ('RR', 'Roraima'),
                ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'),
                ('SE', 'Sergipe'),
                ('TO', 'Tocantins'),
            ]

            # Cidades disponíveis
            cidades_por_estado = {

                'DF': [
                    'Brasília'
                ],

                'GO': [
                    'Águas Lindas de Goiás',
                    'Anápolis',
                    'Aparecida de Goiânia',
                    'Catalão',
                    'Formosa',
                    'Goiânia',
                    'Luziânia',
                    'Planaltina',
                    'Valparaíso de Goiás'
                ],

                'MG': [
                    'Belo Horizonte',
                    'Uberlândia',
                    'Contagem',
                    'Juiz de Fora'
                ],

                'SP': [
                    'São Paulo',
                    'Campinas',
                    'Santos',
                    'Guarulhos'
                ],

                'RJ': [
                    'Rio de Janeiro',
                    'Niterói',
                    'Duque de Caxias'
                ],
            }

            cidades = cidades_por_estado.get(
                dados.get('estado'),
                []
            )

            # -------------------------------------------------
            # BOTÃO VER CIDADES
            # -------------------------------------------------

            acao = request.POST.get('acao')

            if acao == 'ver_cidades':

                return render(request, 'cadastrar.html', {
                    'etapa': '2',
                    'dados': dados,
                    'estados': estados,
                    'cidades': cidades
                })

            # -------------------------------------------------
            # BOTÃO CONTINUAR
            # -------------------------------------------------

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


        # =================================================
        # ETAPA 3 - CONFIRMAÇÃO
        # =================================================

        elif etapa_post == '3':

            senha = request.POST.get(
                'senha',
                ''
            )

            confirmar_senha = request.POST.get(
                'confirmar_senha',
                ''
            )

            # Verifica se as senhas são iguais
            if senha != confirmar_senha:

                return render(request, 'cadastrar.html', {
                    'etapa': '3',
                    'dados': dados,
                    'erro': 'As senhas não são iguais.'
                })

            # Verifica tamanho da senha
            if len(senha) < 8:

                return render(request, 'cadastrar.html', {
                    'etapa': '3',
                    'dados': dados,
                    'erro': (
                        'A senha deve ter pelo menos '
                        '8 caracteres.'
                    )
                })

            # Verifica novamente o e-mail
            if User.objects.filter(
                username=dados.get('email')
            ).exists():

                return render(request, 'cadastrar.html', {
                    'etapa': '3',
                    'dados': dados,
                    'erro': 'Este e-mail já está cadastrado.'
                })

            # Cria o usuário do Django
            usuario = User.objects.create_user(
                username=dados['email'],
                email=dados['email'],
                password=senha,
                first_name=dados['nome']
            )

            # Cria o doador ligado ao usuário
            Doador.objects.create(
                usuario=usuario,
                nome=dados['nome'],
                email=dados['email'],
                telefone=dados.get('telefone', ''),
                tipo_sanguineo=dados.get(
                    'tipo_sanguineo',
                    ''
                ),
                data_nascimento=dados[
                    'data_nascimento'
                ]
            )

            # Limpa os dados temporários
            request.session.pop(
                'cadastro_dados',
                None
            )

            # Vai para o login
            return redirect('login')


    # =====================================================
    # GET
    # =====================================================

    estados = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]

    cidades_por_estado = {

        'DF': [
            'Brasília'
        ],

        'GO': [
            'Águas Lindas de Goiás',
            'Anápolis',
            'Aparecida de Goiânia',
            'Catalão',
            'Formosa',
            'Goiânia',
            'Luziânia',
            'Planaltina',
            'Valparaíso de Goiás'
        ],

        'MG': [
            'Belo Horizonte',
            'Uberlândia',
            'Contagem',
            'Juiz de Fora'
        ],

        'SP': [
            'São Paulo',
            'Campinas',
            'Santos',
            'Guarulhos'
        ],

        'RJ': [
            'Rio de Janeiro',
            'Niterói',
            'Duque de Caxias'
        ],
    }

    cidades = cidades_por_estado.get(
        dados.get('estado'),
        []
    )

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

        # Gera um código de 6 números
        codigo = str(random.randint(100000, 999999))

        # Remove códigos anteriores desse e-mail
        CodigoRecuperacao.objects.filter(
            email=email
        ).delete()

        # Salva o novo código
        CodigoRecuperacao.objects.create(
            email=email,
            codigo=codigo
        )

        # Envia o código por e-mail
        send_mail(
            'Código de verificação - Sangue Bom',
            f'''Olá!

Recebemos uma solicitação para recuperação de senha da sua conta no Sangue Bom.

Seu código de verificação é:

{codigo}

Digite esse código na página de recuperação de senha para confirmar sua solicitação.

Importante: este código é válido por 10 minutos. Após esse período, será necessário solicitar um novo código.

Se você não solicitou a recuperação de senha, ignore este e-mail. Sua senha atual permanecerá inalterada.

Atenciosamente,

Equipe Sangue Bom ❤️

Conectando pessoas à doação de sangue e ajudando a salvar vidas.

''',
            None,
            [email],
            fail_silently=False,
        )

        # Mostra somente a tela do código
        return render(request, 'recuperar_senha.html', {
            'email': email,
            'codigo_enviado': True,
            'mensagem': (
                'Um código de verificação foi enviado '
                'para seu e-mail.'
            )
        })

    return render(request, 'recuperar_senha.html')


# =========================================================
# VALIDAR CÓDIGO
# =========================================================

def validar_codigo(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        codigo_digitado = request.POST.get('codigo')

        # Procura o código salvo no banco
        codigo_recuperacao = CodigoRecuperacao.objects.filter(
            email=email,
            codigo=codigo_digitado
        ).first()

        # Código não encontrado
        if codigo_recuperacao is None:

            return render(request, 'recuperar_senha.html', {
                'erro': 'Código inválido ou incorreto.',
                'email': email,
                'codigo_enviado': True
            })

        # Verifica se o código expirou
        tempo_passado = (
            timezone.now()
            - codigo_recuperacao.criado_em
        )

        if tempo_passado.total_seconds() > 600:

            codigo_recuperacao.delete()

            return render(request, 'recuperar_senha.html', {
                'erro': (
                    'Este código expirou. '
                    'Solicite um novo código.'
                ),
                'email': email
            })

        # Código está correto
        # Agora vai para a tela de nova senha
        return render(request, 'recuperar_senha.html', {
            'email': email,
            'codigo': codigo_digitado,
            'codigo_validado': True,
            'mensagem': 'Código confirmado com sucesso!'
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
        confirmar_senha = request.POST.get(
            'confirmar_senha'
        )

        # Verifica novamente o código
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

        # Verifica se o código expirou
        tempo_passado = (
            timezone.now()
            - codigo_recuperacao.criado_em
        )

        if tempo_passado.total_seconds() > 600:

            codigo_recuperacao.delete()

            return render(request, 'recuperar_senha.html', {
                'erro': (
                    'Este código expirou. '
                    'Solicite um novo código.'
                ),
                'email': email
            })

        # Verifica se as senhas são iguais
        if nova_senha != confirmar_senha:

            return render(request, 'recuperar_senha.html', {
                'erro': 'As senhas não são iguais.',
                'email': email,
                'codigo': codigo,
                'codigo_validado': True
            })

        # Procura o usuário
        usuario = User.objects.filter(
            username=email
        ).first()

        if usuario is None:

            return render(request, 'recuperar_senha.html', {
                'erro': 'Usuário não encontrado.',
                'email': email,
                'codigo': codigo,
                'codigo_validado': True
            })

        # Altera a senha
        usuario.set_password(nova_senha)
        usuario.save()

        # Código não pode ser usado novamente
        codigo_recuperacao.delete()

        # Mostra mensagem de sucesso
        return render(request, 'recuperar_senha.html', {
            'sucesso': (
                'Senha alterada com sucesso! '
                'Você já pode fazer login.'
            )
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

        hemocentro_id = request.POST.get(
            'hemocentro'
        )

        data = request.POST.get(
            'data'
        )

        horario = request.POST.get(
            'horario'
        )

        tipo_doacao = request.POST.get(
            'tipo_doacao'
        )

        # Busca o hemocentro escolhido
        hemocentro = get_object_or_404(
            Hemocentro,
            id=hemocentro_id,
            ativo=True
        )

        # Cria o agendamento
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

    # Data atual
    hoje = timezone.localdate()

    # Busca o próximo agendamento desse doador
    proximo_agendamento = Agendamento.objects.filter(
        doador=doador,
        data__gte=hoje
    ).order_by(
        'data',
        'horario'
    ).first()

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

        hemocentro_id = request.POST.get(
            'hemocentro'
        )

        data = request.POST.get(
            'data'
        )

        horario = request.POST.get(
            'horario'
        )

        tipo_doacao = request.POST.get(
            'tipo_doacao'
        )

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