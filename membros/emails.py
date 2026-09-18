from django.conf import settings
from django.core.mail import send_mail


# =========================================================
# E-MAIL DE CONFIRMAÇÃO DE AGENDAMENTO
# =========================================================

def enviar_email_agendamento(doador, agendamento):
    """
    Envia 2 e-mails:
    1. Confirmação pro DOADOR
    2. Aviso pro HEMOCENTRO
    """

    # ==========================================
    # 📧 E-MAIL 1: PRO DOADOR
    # ==========================================

    assunto_doador = 'Sua doacao foi agendada - Sangue Bom'

    mensagem_doador = f'''Ola, {doador.nome}!

Sua doacao foi agendada com sucesso.

----------------------------------------
DETALHES DO AGENDAMENTO
----------------------------------------
Data: {agendamento.data}
Horario: {agendamento.horario}
Local: {agendamento.hemocentro.nome}
Endereco: {agendamento.hemocentro.endereco}, {agendamento.hemocentro.bairro} - {agendamento.hemocentro.cidade}
Tipo: {agendamento.tipo_doacao}
----------------------------------------

ANTES DE IR, LEMBRE-SE:
- Leve um documento com foto
- Chegue com 15 minutos de antecedencia
- Beba bastante agua antes
- Nao va em jejum
- Evite alimentos gordurosos

----------------------------------------
Contato do hemocentro:
Telefone: {agendamento.hemocentro.telefone}
E-mail: {agendamento.hemocentro.email}
----------------------------------------

Cada doacao pode salvar ate 4 vidas!

Equipe Sangue Bom
'''

    send_mail(
        subject=assunto_doador,
        message=mensagem_doador,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[doador.email],
        fail_silently=False,
    )


    # ==========================================
    # 📧 E-MAIL 2: PRO HEMOCENTRO
    # ==========================================

    assunto_hemocentro = f'Nova doacao agendada - {doador.nome}'

    mensagem_hemocentro = f'''Ola, equipe {agendamento.hemocentro.nome}!

Um novo doador agendou uma doacao no seu hemocentro.

----------------------------------------
DADOS DO DOADOR
----------------------------------------
Nome: {doador.nome}
Tipo sanguineo: {doador.tipo_sanguineo}
Data: {agendamento.data}
Horario: {agendamento.horario}
Tipo de doacao: {agendamento.tipo_doacao}
----------------------------------------

----------------------------------------
CONTATO
----------------------------------------
Telefone: {doador.telefone}
E-mail: {doador.email}
Sexo: {doador.sexo if doador.sexo else "Nao informado"}
----------------------------------------

Prepare o atendimento!

Sistema Sangue Bom
'''

    send_mail(
        subject=assunto_hemocentro,
        message=mensagem_hemocentro,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[agendamento.hemocentro.email],
        fail_silently=False,
    )