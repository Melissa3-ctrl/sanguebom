from django.db import models
from django.contrib.auth.models import User


class Doador(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    nome = models.CharField(max_length=100)

    email = models.EmailField()

    cpf = models.CharField(
        max_length=14,
        unique=True,
        null=True,
        blank=True
    )

    telefone = models.CharField(max_length=20)

    sexo = models.CharField(
        max_length=20,
        blank=True
    )

    tipo_sanguineo = models.CharField(max_length=3)

    data_nascimento = models.DateField()

    cidade = models.CharField(
        max_length=100,
        blank=True
    )

    estado = models.CharField(
        max_length=2,
        blank=True
    )

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

    doador = models.ForeignKey(
        Doador,
        on_delete=models.CASCADE
    )

    hemocentro = models.ForeignKey(
        Hemocentro,
        on_delete=models.CASCADE
    )

    base = models.CharField(
        max_length=100
    )

    data = models.DateField()

    horario = models.TimeField()

    tipo_doacao = models.CharField(
        max_length=30
    )

    def __str__(self):
        return f"{self.doador.nome} - {self.data}"


class CodigoRecuperacao(models.Model):

    email = models.EmailField()

    codigo = models.CharField(
        max_length=6
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email


# =========================================================
# 🆕 NOTIFICAÇÕES
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

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default='alerta'
    )

    titulo = models.CharField(max_length=200)

    mensagem = models.TextField()

    lida = models.BooleanField(default=False)

    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f"{self.titulo} - {self.doador.nome}"