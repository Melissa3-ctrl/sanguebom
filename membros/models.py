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
    telefone = models.CharField(max_length=20)
    tipo_sanguineo = models.CharField(max_length=3)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome


class Hemocentro(models.Model):

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