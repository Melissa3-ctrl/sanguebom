from django.urls import path
from . import views


urlpatterns = [

    # =========================================================
    # PÁGINAS DO SITE
    # =========================================================

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
    # PRECISO DE DOAÇÃO (RECEPTOR) — REATIVADO (SÓ INFO + CADASTRO)
    # O pedido vai SÓ pro admin/hemocentro, não fica visível
    # =========================================================

    path(
        'preciso-doacao/',
        views.preciso_doacao,
        name='preciso_doacao'
    ),

    path(
        'preciso-doacao/cadastrar/',
        views.cadastrar_receptor,
        name='cadastrar_receptor'
    ),

    # As rotas abaixo continuam ESCONDIDAS (não são usadas):

    # path(
    #     'preciso-doacao/<int:id>/',
    #     views.detalhes_receptor,
    #     name='detalhes_receptor'
    # ),

    # path(
    #     'preciso-doacao/<int:id>/ajudar/',
    #     views.quero_ajudar,
    #     name='quero_ajudar'
    # ),


    # =========================================================
    # MEUS PEDIDOS — ESCONDIDO (não é usado)
    # =========================================================

    # path(
    #     'meus-pedidos/',
    #     views.meus_pedidos,
    #     name='meus_pedidos'
    # ),

    # path(
    #     'meus-pedidos/<int:id>/editar/',
    #     views.editar_pedido,
    #     name='editar_pedido'
    # ),

    # path(
    #     'meus-pedidos/<int:id>/excluir/',
    #     views.excluir_pedido,
    #     name='excluir_pedido'
    # ),


    # =========================================================
    # NOTIFICAÇÕES
    # =========================================================

    path(
        'notificacoes/',
        views.notificacoes,
        name='notificacoes'
    ),

    path(
        'notificacoes/<int:id>/lida/',
        views.marcar_lida,
        name='marcar_lida'
    ),

    path(
        'notificacoes/todas-lidas/',
        views.marcar_todas_lidas,
        name='marcar_todas_lidas'
    ),


    # =========================================================
    # RELATÓRIOS (ADMIN) E PAINEL (HEMOCENTRO)
    # =========================================================

    path(
        'relatorios/',
        views.relatorios,
        name='relatorios'
    ),

    path(
        'painel/',
        views.painel_hemocentro,
        name='painel_hemocentro'
    ),


    # =========================================================
    # CRUD DE AGENDAMENTOS
    # =========================================================

    path(
        'agendamentos/',
        views.listar_agendamentos,
        name='listar_agendamentos'
    ),

    path(
        'agendamentos/editar/<int:id>/',
        views.editar_agendamento,
        name='editar_agendamento'
    ),

    path(
        'agendamentos/excluir/<int:id>/',
        views.excluir_agendamento,
        name='excluir_agendamento'
    ),


    # =========================================================
    # PAINEL DO HEMOCENTRO (AÇÕES)
    # =========================================================

    path(
        'painel/status/<int:id>/',
        views.alterar_status,
        name='alterar_status'
    ),

    path(
        'painel/exportar-csv/',
        views.exportar_csv,
        name='exportar_csv'
    ),

]