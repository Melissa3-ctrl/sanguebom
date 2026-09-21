from django.contrib import admin
from .models import Doador, Hemocentro, Agendamento, CodigoRecuperacao, Notificacao


@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo_sanguineo', 'cidade', 'estado')
    list_filter = ('tipo_sanguineo', 'estado')
    search_fields = ('nome', 'email', 'cpf')


@admin.register(Hemocentro)
class HemocentroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'telefone', 'usuario', 'ativo')
    list_filter = ('ativo', 'cidade')
    search_fields = ('nome', 'cidade', 'usuario__username')
    raw_id_fields = ('usuario',)
    fieldsets = (
        ('Dados do Hemocentro', {
            'fields': ('nome', 'endereco', 'bairro', 'cidade', 'cep')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Funcionamento', {
            'fields': ('horario_abertura', 'horario_fechamento', 'dias_atendimento')
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Acesso ao Sistema', {
            'fields': ('usuario', 'ativo'),
            'description': 'O usuário do hemocentro poderá acessar o painel de relatórios.'
        }),
    )


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('doador', 'hemocentro', 'data', 'horario', 'tipo_doacao')
    list_filter = ('tipo_doacao', 'data', 'hemocentro')
    search_fields = ('doador__nome', 'hemocentro__nome')
    date_hierarchy = 'data'


@admin.register(CodigoRecuperacao)
class CodigoRecuperacaoAdmin(admin.ModelAdmin):
    list_display = ('email', 'codigo', 'criado_em')
    search_fields = ('email',)


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'doador', 'tipo', 'lida', 'criada_em')
    list_filter = ('tipo', 'lida', 'criada_em')
    search_fields = ('titulo', 'mensagem', 'doador__nome')
    list_editable = ('lida',)
    date_hierarchy = 'criada_em'