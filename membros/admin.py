import csv
from django.http import HttpResponse
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Doador, Hemocentro, Agendamento, CodigoRecuperacao, Notificacao, Receptor


# =========================================================
# DOADOR
# =========================================================

@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo_sanguineo_badge', 'cidade', 'estado', 'telefone', 'total_agendamentos')
    list_filter = ('tipo_sanguineo', 'estado', 'sexo', 'cidade')
    search_fields = ('nome', 'email', 'cpf', 'telefone')
    list_per_page = 25
    ordering = ('nome',)

    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'email', 'cpf', 'data_nascimento', 'sexo')
        }),
        ('Contato', {
            'fields': ('telefone',)
        }),
        ('Saúde', {
            'fields': ('tipo_sanguineo',)
        }),
        ('Localização', {
            'fields': ('cidade', 'estado')
        }),
        ('Acesso', {
            'fields': ('usuario',)
        }),
    )

    actions = ['exportar_csv']

    def tipo_sanguineo_badge(self, obj):
        cores = {
            'A+': '#d32f2f', 'A-': '#d32f2f',
            'B+': '#1976d2', 'B-': '#1976d2',
            'AB+': '#7b1fa2', 'AB-': '#7b1fa2',
            'O+': '#388e3c', 'O-': '#388e3c',
        }
        cor = cores.get(obj.tipo_sanguineo, '#666')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; border-radius:12px; font-weight:bold;">{}</span>',
            cor, obj.tipo_sanguineo
        )
    tipo_sanguineo_badge.short_description = 'Tipo'

    def total_agendamentos(self, obj):
        return obj.agendamento_set.count()
    total_agendamentos.short_description = 'Agendamentos'

    @admin.action(description='📥 Exportar selecionados para CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="doadores.csv"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Nome', 'Email', 'CPF', 'Telefone', 'Tipo Sanguíneo', 'Cidade', 'Estado'])

        for d in queryset:
            writer.writerow([
                d.nome, d.email, d.cpf or '', d.telefone,
                d.tipo_sanguineo, d.cidade, d.estado
            ])

        return response


# =========================================================
# HEMOCENTRO
# =========================================================

@admin.register(Hemocentro)
class HemocentroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'telefone', 'usuario', 'ativo_badge', 'total_agendamentos')
    list_filter = ('ativo', 'cidade')
    search_fields = ('nome', 'cidade', 'usuario__username')
    raw_id_fields = ('usuario',)
    list_per_page = 25

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

    actions = ['exportar_csv']

    def ativo_badge(self, obj):
        if obj.ativo:
            return format_html('<span style="color:#4caf50; font-weight:bold;">✅ Ativo</span>')
        return format_html('<span style="color:#d32f2f; font-weight:bold;">❌ Inativo</span>')
    ativo_badge.short_description = 'Status'

    def total_agendamentos(self, obj):
        return obj.agendamento_set.count()
    total_agendamentos.short_description = 'Agendamentos'

    @admin.action(description='📥 Exportar selecionados para CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="hemocentros.csv"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Nome', 'Endereço', 'Bairro', 'Cidade', 'CEP', 'Telefone', 'Email', 'Ativo'])

        for h in queryset:
            writer.writerow([
                h.nome, h.endereco, h.bairro, h.cidade, h.cep,
                h.telefone, h.email, 'Sim' if h.ativo else 'Não'
            ])

        return response


# =========================================================
# AGENDAMENTO
# =========================================================

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('data', 'horario', 'doador_link', 'hemocentro', 'tipo_doacao', 'status', 'status_badge')
    list_filter = ('status', 'tipo_doacao', 'data', 'hemocentro')
    search_fields = ('doador__nome', 'doador__email', 'hemocentro__nome')
    date_hierarchy = 'data'
    list_editable = ('status',)
    list_per_page = 25
    raw_id_fields = ('doador', 'hemocentro')
    ordering = ('-data', '-horario')

    actions = ['marcar_realizado', 'marcar_cancelado', 'marcar_faltou', 'marcar_agendado', 'exportar_csv']

    def doador_link(self, obj):
        url = reverse('admin:membros_doador_change', args=[obj.doador.id])
        return format_html('<a href="{}">{}</a>', url, obj.doador.nome)
    doador_link.short_description = 'Doador'

    def status_badge(self, obj):
        cores = {
            'agendado': ('#fff3e0', '#e65100', '⏳'),
            'realizado': ('#e8f5e9', '#2e7d32', '✅'),
            'cancelado': ('#ffebee', '#c62828', '❌'),
            'faltou': ('#f5f5f5', '#616161', '⚠️'),
        }
        bg, cor, icone = cores.get(obj.status, ('#f5f5f5', '#666', ''))
        return format_html(
            '<span style="background:{}; color:{}; padding:3px 10px; border-radius:12px; font-weight:bold;">{} {}</span>',
            bg, cor, icone, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    @admin.action(description='✅ Marcar como Realizado')
    def marcar_realizado(self, request, queryset):
        queryset.update(status='realizado')

    @admin.action(description='❌ Marcar como Cancelado')
    def marcar_cancelado(self, request, queryset):
        queryset.update(status='cancelado')

    @admin.action(description='⚠️ Marcar como Faltou')
    def marcar_faltou(self, request, queryset):
        queryset.update(status='faltou')

    @admin.action(description='⏳ Marcar como Agendado')
    def marcar_agendado(self, request, queryset):
        queryset.update(status='agendado')

    @admin.action(description='📥 Exportar selecionados para CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="agendamentos.csv"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Data', 'Hora', 'Doador', 'Tipo Sanguíneo', 'Hemocentro', 'Tipo Doação', 'Status'])

        for a in queryset:
            writer.writerow([
                a.data, a.horario, a.doador.nome, a.doador.tipo_sanguineo,
                a.hemocentro.nome, a.tipo_doacao, a.get_status_display()
            ])

        return response


# =========================================================
# CÓDIGO RECUPERAÇÃO
# =========================================================

@admin.register(CodigoRecuperacao)
class CodigoRecuperacaoAdmin(admin.ModelAdmin):
    list_display = ('email', 'codigo', 'criado_em')
    search_fields = ('email', 'codigo')
    ordering = ('-criado_em',)
    list_per_page = 25

    actions = ['exportar_csv']

    @admin.action(description='📥 Exportar selecionados para CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="codigos.csv"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Email', 'Código', 'Criado em'])

        for c in queryset:
            writer.writerow([c.email, c.codigo, c.criado_em])

        return response


# =========================================================
# NOTIFICAÇÃO
# =========================================================

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'doador', 'tipo_badge', 'lida', 'lida_badge', 'criada_em')
    list_filter = ('tipo', 'lida', 'criada_em')
    search_fields = ('titulo', 'mensagem', 'doador__nome')
    list_editable = ('lida',)
    date_hierarchy = 'criada_em'
    raw_id_fields = ('doador',)
    list_per_page = 25
    ordering = ('-criada_em',)

    actions = ['exportar_csv']

    def tipo_badge(self, obj):
        return format_html(
            '<span style="background:#f0f0f0; padding:3px 10px; border-radius:12px;">{}</span>',
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'

    def lida_badge(self, obj):
        if obj.lida:
            return format_html('<span style="color:#4caf50;">✅ Lida</span>')
        return format_html('<span style="color:#ff9800;">🔔 Não lida</span>')
    lida_badge.short_description = 'Lida'

    @admin.action(description='📥 Exportar selecionados para CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="notificacoes.csv"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Título', 'Doador', 'Tipo', 'Lida', 'Criada em'])

        for n in queryset:
            writer.writerow([
                n.titulo, n.doador.nome, n.get_tipo_display(),
                'Sim' if n.lida else 'Não', n.criada_em
            ])

        return response


# =========================================================
# 🆕 RECEPTOR (Quem precisa de doação)
# =========================================================

@admin.register(Receptor)
class ReceptorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_sanguineo_badge', 'hospital', 'cidade', 'urgencia_badge', 'ativo', 'criado_em')
    list_filter = ('urgencia', 'ativo', 'cidade', 'tipo_sanguineo')
    search_fields = ('nome', 'hospital', 'cidade', 'contato')
    list_editable = ('ativo',)
    list_per_page = 25
    ordering = ('-urgencia', '-criado_em')
    date_hierarchy = 'criado_em'
    raw_id_fields = ('usuario',)

    fieldsets = (
        ('Dados do Paciente', {
            'fields': ('nome', 'tipo_sanguineo')
        }),
        ('Localização', {
            'fields': ('hospital', 'cidade')
        }),
        ('Urgência', {
            'fields': ('urgencia',)
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Contato', {
            'fields': ('contato',)
        }),
        ('Acesso', {
            'fields': ('usuario', 'ativo'),
            'description': 'O receptor só aparece no site se estiver ATIVO.'
        }),
    )

    actions = ['aprovar', 'reprovar', 'exportar_csv']

    def tipo_sanguineo_badge(self, obj):
        cores = {
            'A+': '#d32f2f', 'A-': '#d32f2f',
            'B+': '#1976d2', 'B-': '#1976d2',
            'AB+': '#7b1fa2', 'AB-': '#7b1fa2',
            'O+': '#388e3c', 'O-': '#388e3c',
        }
        cor = cores.get(obj.tipo_sanguineo, '#666')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; border-radius:12px; font-weight:bold;">{}</span>',
            cor, obj.tipo_sanguineo
        )
    tipo_sanguineo_badge.short_description = 'Tipo'

    def urgencia_badge(self, obj):
        cores = {
            'baixa': ('#e8f5e9', '#2e7d32', '🟢'),
            'media': ('#fff3e0', '#e65100', '🟡'),
            'alta': ('#ffebee', '#c62828', '🔴'),
        }
        bg, cor, icone = cores.get(obj.urgencia, ('#f5f5f5', '#666', ''))
        return format_html(
            '<span style="background:{}; color:{}; padding:3px 10px; border-radius:12px; font-weight:bold;">{} {}</span>',
            bg, cor, icone, obj.get_urgencia_display()
        )
    urgencia_badge.short_description = 'Urgência'

    @admin.action(description='✅ Aprovar selecionados')
    def aprovar(self, request, queryset):
        queryset.update(ativo=True)

    @admin.action(description='❌ Reprovar selecionados')
    def reprovar(self, request, queryset):
        queryset.update(ativo=False)

    @admin.action(description='📥 Exportar selecionados para CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="receptores.csv"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Nome', 'Tipo Sanguíneo', 'Hospital', 'Cidade', 'Urgência', 'Contato', 'Ativo'])

        for r in queryset:
            writer.writerow([
                r.nome, r.tipo_sanguineo, r.hospital, r.cidade,
                r.get_urgencia_display(), r.contato,
                'Sim' if r.ativo else 'Não'
            ])

        return response