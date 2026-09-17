from django.urls import path
from . import views


urlpatterns = [

    # =========================================================
    # PÁGINAS DO SITE
    # =========================================================

    # Raiz abre a home direto
    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'home/',
        views.home,
        name='home'
    ),

    path(
        'quero_doar/',
        views.quero_doar,
        name='quero_doar'
    ),

    path(
        'tipos_sanguineos/',
        views.tipos_sanguineos,
        name='tipos_sanguineos'
    ),

    path(
        'notificacoes/',
        views.notificacoes,
        name='notificacoes'
    ),

    path(
        'cadastro/',
        views.cadastro,
        name='cadastro'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'recuperar_senha/',
        views.recuperar_senha,
        name='recuperar_senha'
    ),

    path(
        'validar_codigo/',
        views.validar_codigo,
        name='validar_codigo'
    ),

    # 👇 NOVA ROTA: REENVIAR CÓDIGO
    path(
        'reenviar_codigo/',
        views.reenviar_codigo,
        name='reenviar_codigo'
    ),

    path(
        'alterar_senha/',
        views.alterar_senha,
        name='alterar_senha'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    path(
        'beneficios/',
        views.beneficios,
        name='beneficios'
    ),

    path(
        'campanhas/',
        views.campanhas,
        name='campanhas'
    ),

    path(
        'duvidas/',
        views.duvidas,
        name='duvidas'
    ),

    path(
        'locais_para_doar/',
        views.locais_para_doar,
        name='locais_para_doar'
    ),

    path(
        'meu_perfil/',
        views.meu_perfil,
        name='meu_perfil'
    ),

    path(
        'agendar_doacao/',
        views.agendar_doacao,
        name='agendar_doacao'
    ),


    # =========================================================
    # CRUD DE AGENDAMENTOS
    # =========================================================

    # READ - listar
    path(
        'agendamentos/',
        views.listar_agendamentos,
        name='listar_agendamentos'
    ),

    # UPDATE - editar
    path(
        'agendamentos/editar/<int:id>/',
        views.editar_agendamento,
        name='editar_agendamento'
    ),

    # DELETE - excluir
    path(
        'agendamentos/excluir/<int:id>/',
        views.excluir_agendamento,
        name='excluir_agendamento'
    ),

]