from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Doador(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=20)
    sexo = models.CharField(max_length=20, blank=True)
    tipo_sanguineo = models.CharField(max_length=3)
    data_nascimento = models.DateField()
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return self.nome


class Hemocentro(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hemocentro'
    )

    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    cep = models.CharField(max_length=10)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    horario_abertura = models.TimeField()
    horario_fechamento = models.TimeField()
    dias_atendimento = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Agendamento(models.Model):

    STATUS = [
        ('agendado', '⏳ Agendado'),
        ('realizado', '✅ Realizado'),
        ('cancelado', '❌ Cancelado'),
        ('faltou', '⚠️ Faltou'),
    ]

    doador = models.ForeignKey(Doador, on_delete=models.CASCADE)
    hemocentro = models.ForeignKey(Hemocentro, on_delete=models.CASCADE)
    base = models.CharField(max_length=100)
    data = models.DateField()
    horario = models.TimeField()
    tipo_doacao = models.CharField(max_length=30)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='agendado'
    )

    def __str__(self):
        return f"{self.doador.nome} - {self.data}"


class CodigoRecuperacao(models.Model):

    email = models.EmailField()
    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# =========================================================
# NOTIFICAÇÕES
# =========================================================

class Notificacao(models.Model):

    TIPOS = [
        ('alerta', '🚨 Alerta'),
        ('lembrete', '📅 Lembrete'),
        ('campanha', '🩸 Campanha'),
        ('confirmado', '✅ Confirmação'),
        ('nivel', '🏆 Nível'),
    ]

    doador = models.ForeignKey(
        Doador,
        on_delete=models.CASCADE,
        related_name='notificacoes'
    )

    tipo = models.CharField(max_length=20, choices=TIPOS, default='alerta')
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f"{self.titulo} - {self.doador.nome}"


# =========================================================
# RECEPTOR (Quem precisa de doação)
# =========================================================

class Receptor(models.Model):

    URGENCIA = [
        ('baixa', '🟢 Baixa'),
        ('media', '🟡 Média'),
        ('alta', '🔴 Alta'),
    ]

    STATUS = [
        ('pendente', '⏳ Pendente'),
        ('aprovado', '✅ Aprovado'),
        ('atendido', '🎉 Atendido'),
        ('expirado', '📅 Expirado'),
        ('recusado', '❌ Recusado'),
    ]

    TIPOS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    TIPOS_DOACAO = [
        ('sangue', '🩸 Sangue Total'),
        ('plaquetas', '🟡 Plaquetas'),
        ('plasma', '🟠 Plasma'),
        ('medula', '🦴 Medula Óssea'),
        ('hemacias', '🔴 Concentrado de Hemácias'),
    ]

    SEXO = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='receptores'
    )

    nome = models.CharField(max_length=100)

    idade_paciente = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Idade do paciente'
    )

    sexo_paciente = models.CharField(
        max_length=20,
        blank=True,
        choices=SEXO,
        verbose_name='Sexo do paciente'
    )

    tipo_sanguineo = models.CharField(max_length=3, choices=TIPOS)

    tipo_doacao = models.CharField(
        max_length=20,
        choices=TIPOS_DOACAO,
        default='sangue',
        verbose_name='Tipo de doação necessária'
    )

    hospital = models.CharField(max_length=200)

    cidade = models.CharField(max_length=100)

    urgencia = models.CharField(max_length=20, choices=URGENCIA, default='media')

    descricao = models.TextField()

    # CONTATO SEPARADO (email + celular)
    email_contato = models.EmailField(
        blank=True,
        verbose_name='E-mail do responsável'
    )

    celular_contato = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Celular do responsável'
    )

    contato = models.CharField(max_length=200, blank=True)

    # LAUDO MÉDICO (upload)
    laudo = models.FileField(
        upload_to='laudos/',
        blank=True,
        null=True,
        verbose_name='Laudo médico',
        help_text='Anexe o laudo médico ou documento que comprove o caso'
    )

    status = models.CharField(max_length=20, choices=STATUS, default='pendente')

    ativo = models.BooleanField(default=False)

    visualizacoes = models.PositiveIntegerField(default=0)

    criado_em = models.DateTimeField(auto_now_add=True)

    expira_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-urgencia', '-criado_em']

    def save(self, *args, **kwargs):
        if not self.expira_em:
            self.expira_em = timezone.now() + timedelta(days=30)

        if self.expira_em and timezone.now() > self.expira_em and self.status == 'aprovado':
            self.status = 'expirado'
            self.ativo = False

        super().save(*args, **kwargs)

    @property
    def expirado(self):
        if self.expira_em and timezone.now() > self.expira_em:
            return True
        return False

    @property
    def dias_restantes(self):
        if self.expira_em:
            delta = self.expira_em - timezone.now()
            return max(0, delta.days)
        return 0

    def __str__(self):
        return f"{self.nome} - {self.tipo_sanguineo}"

    # =========================================================
# CAMPANHA (Eventos e ações do hemocentro)
# =========================================================

class Campanha(models.Model):

    STATUS = [
        ('ativa', '✅ Ativa'),
        ('breve', '📅 Em breve'),
        ('urgente', '🚨 Urgente'),
        ('encerrada', '❌ Encerrada'),
    ]

    emoji = models.CharField(max_length=10, default='🩸', verbose_name='Emoji')

    titulo = models.CharField(max_length=200, verbose_name='Título')

    descricao = models.TextField(verbose_name='Descrição')

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='ativa',
        verbose_name='Status'
    )

    local = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Local'
    )

    data = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Data / Período'
    )

    ativa = models.BooleanField(default=True, verbose_name='Visível no site')

    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Campanha'
        verbose_name_plural = 'Campanhas'

    def __str__(self):
        return self.titulo