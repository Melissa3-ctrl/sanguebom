from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from datetime import timedelta, datetime
from .models import Agendamento


# =========================================================
# FUNÇÃO AUXILIAR: CALCULA NÍVEL
# =========================================================

def calcular_nivel(total):
    """Retorna (nivel, proximo_nivel, faltam, progresso, emoji)"""
    if total >= 6:
        return ('Ouro', None, 0, 100, '🥇')
    elif total >= 3:
        return ('Prata', 'Ouro', 6 - total, int((total / 6) * 100), '🥈')
    else:
        return ('Bronze', 'Prata', 3 - total, int((total / 3) * 100), '🥉')


# =========================================================
# E-MAIL DE CONFIRMAÇÃO DE AGENDAMENTO
# =========================================================

def enviar_email_agendamento(doador, agendamento):
    """
    Envia 2 e-mails HTML bonitos:
    1. Confirmação pro DOADOR (com nível + benefícios completos)
    2. Aviso pro HEMOCENTRO (e-mail do hemocentro escolhido)
    """

    # ==========================================
    # 📊 CALCULA O PROGRESSO DO DOADOR
    # ==========================================

    total = Agendamento.objects.filter(doador=doador, status='realizado').count()
    nivel, proximo, faltam, progresso, emoji = calcular_nivel(total)

    # Monta o assunto dinâmico
    if proximo:
        if faltam == 1:
            assunto_doador = f'{emoji} Agendamento confirmado! Você está no {nivel} — Falta 1 pro {proximo} 🩸'
            msg_falta = f'Falta <strong>1 doação</strong> pro {proximo}!'
            texto_falta = f'Falta 1 pro {proximo}'
        else:
            assunto_doador = f'{emoji} Agendamento confirmado! Você está no {nivel} — Faltam {faltam} pro {proximo} 🩸'
            msg_falta = f'Faltam <strong>{faltam} doações</strong> pro {proximo}!'
            texto_falta = f'Faltam {faltam} pro {proximo}'
    else:
        assunto_doador = f'{emoji} Agendamento confirmado! Você está no {nivel} — Você é incrível! 🏆🩸'
        msg_falta = '🏆 Você atingiu o <strong>nível máximo</strong>!'
        texto_falta = 'Você atingiu o nível máximo!'

    # ==========================================
    # 📧 E-MAIL 1: PRO DOADOR
    # ==========================================

    html_doador = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="margin:0; padding:0; font-family:Arial, Helvetica, sans-serif; background:#fcf9f2;">

    <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.08);">

        <div style="background:linear-gradient(135deg, #b30000, #7a0000); padding:35px 30px; text-align:center; color:#ffffff;">
            <h1 style="margin:0; font-size:28px; font-weight:bold;">🩸 Sangue Bom</h1>
            <p style="margin:10px 0 0 0; opacity:0.9; font-size:14px;">Sua doação foi agendada com sucesso!</p>
        </div>

        <div style="padding:40px 30px;">

            <h2 style="color:#b30000; margin-top:0; font-size:22px;">Olá, {doador.nome}! 👋</h2>

            <p style="color:#555555; font-size:16px; line-height:1.6;">
                Sua doação foi <strong style="color:#008000;">agendada com sucesso</strong>! ✅
            </p>

            <p style="color:#555555; font-size:16px; line-height:1.6;">
                Confira os detalhes abaixo:
            </p>

            <div style="background:#fcf9f2; border-left:4px solid #b30000; padding:20px; border-radius:12px; margin:25px 0;">
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>📅 Data:</strong> {agendamento.data}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>🕐 Horário:</strong> {agendamento.horario}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>🏥 Local:</strong> {agendamento.hemocentro.nome}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>📍 Endereço:</strong> {agendamento.hemocentro.endereco}, {agendamento.hemocentro.bairro} - {agendamento.hemocentro.cidade}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>🩸 Tipo:</strong> {agendamento.tipo_doacao}</p>
            </div>

            <!-- PROGRESSO -->
            <div style="background:#fff5f5; border:2px solid #b30000; border-radius:12px; padding:25px; margin:30px 0;">
                <h3 style="margin:0 0 15px 0; color:#b30000; font-size:18px; text-align:center;">
                    {emoji} Seu progresso de doador
                </h3>

                <p style="margin:0 0 10px 0; color:#333333; font-size:15px; text-align:center;">
                    Você já fez <strong>{total} doação{'ões' if total != 1 else ''}</strong> realizadas
                </p>

                <div style="background:#eeeeee; border-radius:20px; height:24px; overflow:hidden; margin:15px 0;">
                    <div style="background:linear-gradient(90deg, #b30000, #ff6b6b); height:100%; width:{progresso}%; border-radius:20px;"></div>
                </div>

                <p style="margin:10px 0; color:#333333; font-size:15px; text-align:center;">
                    <strong>{progresso}%</strong> — Nível: <strong>{emoji} {nivel}</strong>
                </p>

                <p style="margin:10px 0 0 0; color:#666666; font-size:14px; text-align:center;">
                    {msg_falta}
                </p>
            </div>

            <!-- BENEFÍCIOS -->
            <h3 style="color:#b30000; font-size:16px; margin-top:30px; text-align:center;">
                🎁 Veja o que você ganha em cada nível
            </h3>

            <div style="background:#fdf5ea; border-left:4px solid #cd7f32; border-radius:10px; padding:15px 18px; margin:12px 0;">
                <p style="margin:0 0 8px 0; color:#cd7f32; font-size:15px; font-weight:bold;">🥉 BRONZE (1 a 2 doações)</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Certificado digital de doador</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Acesso ao ranking de doadores</p>
            </div>

            <div style="background:#f5f5f5; border-left:4px solid #a0a0a0; border-radius:10px; padding:15px 18px; margin:12px 0;">
                <p style="margin:0 0 8px 0; color:#7a7a7a; font-size:15px; font-weight:bold;">🥈 PRATA (3 a 5 doações)</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Todos os benefícios do Bronze</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Desconto em eventos culturais</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Prioridade em vacinação</p>
            </div>

            <div style="background:#fffbe6; border-left:4px solid #ffd700; border-radius:10px; padding:15px 18px; margin:12px 0;">
                <p style="margin:0 0 8px 0; color:#b8860b; font-size:15px; font-weight:bold;">🥇 OURO (6 ou mais doações)</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Todos os benefícios do Prata</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Isenção em concursos do DF</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Meia-entrada em eventos culturais</p>
                <p style="margin:4px 0; color:#555555; font-size:14px;">✅ Selo "Doador Ouro" no perfil</p>
            </div>

            <!-- BOTÃO -->
            <div style="text-align:center; margin:30px 0;">
                <a href="http://127.0.0.1:8000/beneficios/" style="display:inline-block; background:#b30000; color:#ffffff; padding:14px 32px; border-radius:50px; text-decoration:none; font-weight:bold; font-size:15px;">
                    🎁 Ver meus benefícios
                </a>
            </div>

            <!-- ANTES DE DOAR -->
            <h3 style="color:#b30000; font-size:16px; margin-top:30px;">📋 Antes de ir, lembre-se:</h3>
            <ul style="color:#555555; line-height:1.9; padding-left:20px; font-size:15px;">
                <li>Leve um documento com foto</li>
                <li>Chegue com 15 minutos de antecedência</li>
                <li>Beba bastante água antes</li>
                <li>Não vá em jejum</li>
                <li>Evite alimentos gordurosos</li>
            </ul>

            <p style="color:#888888; font-size:14px; text-align:center; margin-top:35px; font-style:italic;">
                💗 Cada doação pode salvar até 4 vidas!
            </p>

        </div>

        <div style="background:#7a0000; color:rgba(255,255,255,0.85); padding:25px 20px; text-align:center; font-size:13px;">
            <p style="margin:5px 0;"><strong>Contato do hemocentro:</strong></p>
            <p style="margin:5px 0;">📞 {agendamento.hemocentro.telefone}</p>
            <p style="margin:5px 0;">📧 {agendamento.hemocentro.email}</p>
            <p style="margin:18px 0 0 0; opacity:0.7; font-size:12px;">Equipe Sangue Bom 💗</p>
        </div>

    </div>

</body>
</html>
'''

    texto_doador = f'''Olá, {doador.nome}!

Sua doação foi agendada com sucesso!

Data: {agendamento.data}
Horário: {agendamento.horario}
Local: {agendamento.hemocentro.nome}
Tipo: {agendamento.tipo_doacao}

Seu progresso: {total} doação(ões) realizadas — Nível {nivel} ({progresso}%)
{texto_falta}

BENEFÍCIOS POR NÍVEL:
🥉 Bronze: Certificado digital + Acesso ao ranking
🥈 Prata: + Desconto em eventos + Prioridade em vacinação
🥇 Ouro: + Isenção em concursos + Meia-entrada + Selo Ouro

Antes de ir, lembre-se:
- Leve um documento com foto
- Chegue com 15 minutos de antecedência
- Beba bastante água antes
- Não vá em jejum

Equipe Sangue Bom 💗
'''

    email_doador = EmailMultiAlternatives(
        subject=assunto_doador,
        body=texto_doador,
        from_email=settings.EMAIL_HOST_USER,
        to=[doador.email]
    )
    email_doador.attach_alternative(html_doador, "text/html")
    email_doador.send(fail_silently=False)


    # ==========================================
    # 📧 E-MAIL 2: PRO HEMOCENTRO
    # ==========================================

    assunto_hemocentro = f'🩸 Nova doação agendada - {doador.nome}'

    html_hemocentro = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="margin:0; padding:0; font-family:Arial, Helvetica, sans-serif; background:#fcf9f2;">

    <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.08);">

        <div style="background:linear-gradient(135deg, #b30000, #7a0000); padding:35px 30px; text-align:center; color:#ffffff;">
            <h1 style="margin:0; font-size:24px;">🩸 Nova Doação Agendada</h1>
            <p style="margin:10px 0 0 0; opacity:0.9; font-size:14px;">{agendamento.hemocentro.nome}</p>
        </div>

        <div style="padding:40px 30px;">

            <p style="color:#555555; font-size:16px; line-height:1.6;">
                Olá, equipe! 👋
            </p>

            <p style="color:#555555; font-size:16px; line-height:1.6;">
                Um novo doador agendou uma doação no seu hemocentro. Confira os dados:
            </p>

            <div style="background:#fcf9f2; border-left:4px solid #b30000; padding:20px; border-radius:12px; margin:25px 0;">
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>👤 Nome:</strong> {doador.nome}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>🩸 Tipo sanguíneo:</strong> <span style="background:#b30000; color:#ffffff; padding:3px 12px; border-radius:12px; font-weight:bold; font-size:14px;">{doador.tipo_sanguineo}</span></p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>📅 Data:</strong> {agendamento.data}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>🕐 Horário:</strong> {agendamento.horario}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>🩸 Tipo de doação:</strong> {agendamento.tipo_doacao}</p>
                <hr style="border:none; border-top:1px solid #e0e0e0; margin:18px 0;">
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>📞 Telefone:</strong> {doador.telefone}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>📧 E-mail:</strong> {doador.email}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>💬 Sexo:</strong> {doador.sexo if doador.sexo else "Não informado"}</p>
                <p style="margin:8px 0; color:#333333; font-size:15px;"><strong>{emoji} Nível:</strong> {nivel} ({total} doação{'ões' if total != 1 else ''} realizadas)</p>
            </div>

            <p style="color:#2e7d32; font-size:15px; text-align:center; padding:18px; background:#e8f5e9; border-radius:10px; margin:25px 0;">
                ✅ <strong>Prepare o atendimento!</strong><br>
                <span style="font-size:13px; opacity:0.8;">O doador chegará no horário agendado.</span>
            </p>

        </div>

        <div style="background:#7a0000; color:rgba(255,255,255,0.85); padding:25px 20px; text-align:center; font-size:13px;">
            <p style="margin:0; font-weight:bold;">Sistema Sangue Bom 💗</p>
            <p style="margin:12px 0 0 0; opacity:0.7; font-size:12px;">Este é um e-mail automático.</p>
        </div>

    </div>

</body>
</html>
'''

    texto_hemocentro = f'''Nova doação agendada!

Nome: {doador.nome}
Tipo sanguíneo: {doador.tipo_sanguineo}
Data: {agendamento.data}
Horário: {agendamento.horario}
Tipo de doação: {agendamento.tipo_doacao}
Telefone: {doador.telefone}
E-mail: {doador.email}
Nível: {nivel} ({total} doações realizadas)

Sistema Sangue Bom 💗
'''

    email_hemocentro = EmailMultiAlternatives(
        subject=assunto_hemocentro,
        body=texto_hemocentro,
        from_email=settings.EMAIL_HOST_USER,
        to=[agendamento.hemocentro.email]
    )
    email_hemocentro.attach_alternative(html_hemocentro, "text/html")
    email_hemocentro.send(fail_silently=False)


# =========================================================
# E-MAIL DE DOAÇÃO REALIZADA (agradecimento + próxima doação + exame)
# =========================================================

def enviar_email_doacao_realizada(doador, agendamento):
    """
    Envia e-mail pro doador quando o hemocentro marca como REALIZADO.
    Mostra agradecimento + nível + benefícios + próxima doação + exame.
    """

    total = Agendamento.objects.filter(doador=doador, status='realizado').count()
    nivel, proximo, faltam, progresso, emoji = calcular_nivel(total)

    # ==========================================
    # 📅 CALCULA PRÓXIMA DOAÇÃO E DATA DO EXAME
    # ==========================================

    # Dias de espera por sexo
    if doador.sexo == 'M':
        dias_espera = 60
        texto_sexo = 'Homens podem doar a cada 60 dias'
    elif doador.sexo == 'F':
        dias_espera = 90
        texto_sexo = 'Mulheres podem doar a cada 90 dias'
    else:
        dias_espera = 90
        texto_sexo = 'Recomendação padrão: 90 dias'

    # Data base da doação (aceita date ou string)
    data_base = agendamento.data
    if isinstance(data_base, str):
        data_base = datetime.strptime(data_base, '%Y-%m-%d').date()

    # Calcula datas
    proxima_doacao = data_base + timedelta(days=dias_espera)
    data_exame = data_base + timedelta(days=9)

    # Formata
    proxima_doacao_fmt = proxima_doacao.strftime('%d/%m/%Y')
    data_exame_fmt = data_exame.strftime('%d/%m/%Y')

    # Assunto dinâmico
    if proximo:
        if faltam == 1:
            assunto = f'❤️ Obrigado por doar! Você está no {nivel} — Falta 1 pro {proximo} 🩸'
        else:
            assunto = f'❤️ Obrigado por doar! Você está no {nivel} — Faltam {faltam} pro {proximo} 🩸'
    else:
        assunto = f'🏆 Obrigado por doar! Você atingiu o nível OURO! 🩸'

    # Mensagem de falta
    if proximo:
        msg_falta = f'Faltam <strong>{faltam} doações</strong> pro nível {proximo} {emoji}'
    else:
        msg_falta = '🏆 Você atingiu o <strong>nível máximo</strong>!'

    # Benefícios por nível (HTML)
    if nivel == 'Bronze':
        beneficios_html = '''
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Certificado digital de doador</p>
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Acesso ao ranking de doadores</p>
        '''
    elif nivel == 'Prata':
        beneficios_html = '''
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Todos os benefícios do Bronze</p>
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Desconto em eventos culturais</p>
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Prioridade em vacinação</p>
        '''
    else:
        beneficios_html = '''
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Todos os benefícios do Prata</p>
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Isenção em concursos do DF</p>
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Meia-entrada em eventos culturais</p>
        <p style="margin:6px 0; color:#555555; font-size:15px;">✅ Selo "Doador Ouro" no perfil</p>
        '''

    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="margin:0; padding:0; font-family:Arial, Helvetica, sans-serif; background:#fcf9f2;">

    <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.08);">

        <div style="background:linear-gradient(135deg, #b30000, #7a0000); padding:40px 30px; text-align:center; color:#ffffff;">
            <div style="font-size:60px; margin-bottom:10px;">❤️</div>
            <h1 style="margin:0; font-size:28px; font-weight:bold;">Obrigado por doar!</h1>
            <p style="margin:10px 0 0 0; opacity:0.9; font-size:15px;">Sua doação foi registrada com sucesso</p>
        </div>

        <div style="padding:40px 30px;">

            <h2 style="color:#b30000; margin-top:0; font-size:22px;">Olá, {doador.nome}! 👋</h2>

            <p style="color:#555555; font-size:16px; line-height:1.6;">
                Sua doação no <strong>{agendamento.hemocentro.nome}</strong> foi <strong style="color:#008000;">confirmada</strong>!
            </p>

            <div style="background:#e8f5e9; border-left:4px solid #4caf50; padding:20px; border-radius:12px; margin:25px 0; text-align:center;">
                <p style="margin:0; color:#2e7d32; font-size:16px; line-height:1.6;">
                    💗 <strong>Você acabou de salvar até 4 vidas!</strong>
                </p>
                <p style="margin:8px 0 0 0; color:#555555; font-size:14px;">
                    Obrigado por fazer a diferença na vida de outras pessoas.
                </p>
            </div>

            <!-- PROGRESSO -->
            <div style="background:#fff5f5; border:2px solid #b30000; border-radius:12px; padding:25px; margin:30px 0;">
                <h3 style="margin:0 0 15px 0; color:#b30000; font-size:18px; text-align:center;">
                    {emoji} Seu progresso de doador
                </h3>

                <p style="margin:0 0 10px 0; color:#333333; font-size:15px; text-align:center;">
                    Você já fez <strong>{total} doação{'ões' if total != 1 else ''}</strong> realizadas
                </p>

                <div style="background:#eeeeee; border-radius:20px; height:24px; overflow:hidden; margin:15px 0;">
                    <div style="background:linear-gradient(90deg, #b30000, #ff6b6b); height:100%; width:{progresso}%; border-radius:20px;"></div>
                </div>

                <p style="margin:10px 0; color:#333333; font-size:15px; text-align:center;">
                    <strong>{progresso}%</strong> — Nível: <strong>{emoji} {nivel}</strong>
                </p>

                <p style="margin:10px 0 0 0; color:#666666; font-size:14px; text-align:center;">
                    {msg_falta}
                </p>
            </div>

            <!-- PRÓXIMA DOAÇÃO -->
            <div style="background:#f0f7ff; border-left:4px solid #1976d2; border-radius:12px; padding:20px; margin:25px 0;">
                <h3 style="margin:0 0 10px 0; color:#1565c0; font-size:17px;">
                    📅 Próxima doação disponível
                </h3>
                <p style="margin:6px 0; color:#333333; font-size:15px; line-height:1.6;">
                    Você poderá doar novamente a partir de:
                </p>
                <p style="margin:10px 0; color:#1565c0; font-size:22px; font-weight:bold; text-align:center;">
                    {proxima_doacao_fmt}
                </p>
                <p style="margin:8px 0 0 0; color:#666666; font-size:13px; text-align:center; font-style:italic;">
                    ({texto_sexo})
                </p>
            </div>

            <!-- EXAME DISPONÍVEL -->
            <div style="background:#fff8e1; border-left:4px solid #ffc107; border-radius:12px; padding:20px; margin:25px 0;">
                <h3 style="margin:0 0 10px 0; color:#b8860b; font-size:17px;">
                    📋 Exame disponível
                </h3>
                <p style="margin:6px 0; color:#333333; font-size:15px; line-height:1.6;">
                    Os resultados dos exames da sua doação estarão disponíveis a partir de:
                </p>
                <p style="margin:10px 0; color:#b8860b; font-size:22px; font-weight:bold; text-align:center;">
                    {data_exame_fmt}
                </p>
                <p style="margin:8px 0 0 0; color:#666666; font-size:13px; text-align:center; line-height:1.5;">
                    Procure o <strong>{agendamento.hemocentro.nome}</strong> para retirar o resultado.<br>
                    📞 {agendamento.hemocentro.telefone}
                </p>
            </div>

            <!-- BENEFÍCIOS -->
            <h3 style="color:#b30000; font-size:16px; margin-top:30px; text-align:center;">
                🎁 Seus benefícios desbloqueados no nível {nivel}
            </h3>

            <div style="background:#fff5f5; border:2px solid #b30000; border-radius:12px; padding:20px; margin:20px 0;">
                {beneficios_html}
            </div>

            <!-- BOTÃO -->
            <div style="text-align:center; margin:30px 0;">
                <a href="http://127.0.0.1:8000/beneficios/" style="display:inline-block; background:#b30000; color:#ffffff; padding:14px 32px; border-radius:50px; text-decoration:none; font-weight:bold; font-size:15px;">
                    🎁 Ver meus benefícios
                </a>
            </div>

            <p style="color:#888888; font-size:14px; text-align:center; margin-top:35px; font-style:italic;">
                💗 Cada doação pode salvar até 4 vidas!
            </p>

        </div>

        <div style="background:#7a0000; color:rgba(255,255,255,0.85); padding:25px 20px; text-align:center; font-size:13px;">
            <p style="margin:0; font-weight:bold;">Sangue Bom 💗</p>
            <p style="margin:12px 0 0 0; opacity:0.7; font-size:12px;">Doe sangue. Doe vida.</p>
        </div>

    </div>

</body>
</html>
'''

    texto = f'''Olá, {doador.nome}!

Sua doação no {agendamento.hemocentro.nome} foi confirmada! ❤️

Você acabou de salvar até 4 vidas!

Seu progresso: {total} doação(ões) realizadas — Nível {nivel} ({progresso}%)
{'Faltam ' + str(faltam) + ' doações pro nível ' + proximo if proximo else 'Você atingiu o nível máximo!'}

PRÓXIMA DOAÇÃO:
Você poderá doar novamente a partir de {proxima_doacao_fmt}
({texto_sexo})

EXAME DISPONÍVEL:
Os resultados estarão disponíveis a partir de {data_exame_fmt}
Procure o {agendamento.hemocentro.nome} para retirar.
📞 {agendamento.hemocentro.telefone}

Equipe Sangue Bom 💗
'''

    email = EmailMultiAlternatives(
        subject=assunto,
        body=texto,
        from_email=settings.EMAIL_HOST_USER,
        to=[doador.email]
    )
    email.attach_alternative(html, "text/html")
    email.send(fail_silently=False)