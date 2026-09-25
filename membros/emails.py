from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from datetime import timedelta, datetime
from .models import Agendamento


def calcular_nivel(total):
    if total >= 6:
        return ('Ouro', None, 0, 100, '🥇')
    elif total >= 3:
        return ('Prata', 'Ouro', 6 - total, int((total / 6) * 100), '🥈')
    else:
        return ('Bronze', 'Prata', 3 - total, int((total / 3) * 100), '🥉')


def enviar_email_agendamento(doador, agendamento):
    total = Agendamento.objects.filter(doador=doador, status='realizado').count()
    nivel, proximo, faltam, progresso, emoji = calcular_nivel(total)

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

    html_doador = f'''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:Arial, sans-serif; background:#fcf9f2;">
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
            <div style="background:#fcf9f2; border-left:4px solid #b30000; padding:20px; border-radius:12px; margin:25px 0;">
                <p style="margin:8px 0; color:#333; font-size:15px;"><strong>📅 Data:</strong> {agendamento.data}</p>
                <p style="margin:8px 0; color:#333; font-size:15px;"><strong>🕐 Horário:</strong> {agendamento.horario}</p>
                <p style="margin:8px 0; color:#333; font-size:15px;"><strong>🏥 Local:</strong> {agendamento.hemocentro.nome}</p>
                <p style="margin:8px 0; color:#333; font-size:15px;"><strong>📍 Endereço:</strong> {agendamento.hemocentro.endereco}, {agendamento.hemocentro.bairro} - {agendamento.hemocentro.cidade}</p>
                <p style="margin:8px 0; color:#333; font-size:15px;"><strong>🩸 Tipo:</strong> {agendamento.tipo_doacao}</p>
            </div>
            <div style="background:#fff5f5; border:2px solid #b30000; border-radius:12px; padding:25px; margin:30px 0;">
                <h3 style="margin:0 0 15px 0; color:#b30000; font-size:18px; text-align:center;">{emoji} Seu progresso de doador</h3>
                <p style="margin:0 0 10px 0; color:#333; font-size:15px; text-align:center;">Você já fez <strong>{total} doação{'ões' if total != 1 else ''}</strong> realizadas</p>
                <div style="background:#eeeeee; border-radius:20px; height:24px; overflow:hidden; margin:15px 0;">
                    <div style="background:linear-gradient(90deg, #b30000, #ff6b6b); height:100%; width:{progresso}%; border-radius:20px;"></div>
                </div>
                <p style="margin:10px 0; color:#333; font-size:15px; text-align:center;"><strong>{progresso}%</strong> — Nível: <strong>{emoji} {nivel}</strong></p>
                <p style="margin:10px 0 0 0; color:#666; font-size:14px; text-align:center;">{msg_falta}</p>
            </div>
            <h3 style="color:#b30000; font-size:16px; margin-top:30px; text-align:center;">🎁 Veja o que você ganha em cada nível</h3>
            <div style="background:#fdf5ea; border-left:4px solid #cd7f32; border-radius:10px; padding:15px 18px; margin:12px 0;">
                <p style="margin:0 0 8px 0; color:#cd7f32; font-size:15px; font-weight:bold;">🥉 BRONZE (1 a 2 doações)</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Certificado digital de doador</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Acesso ao ranking de doadores</p>
            </div>
            <div style="background:#f5f5f5; border-left:4px solid #a0a0a0; border-radius:10px; padding:15px 18px; margin:12px 0;">
                <p style="margin:0 0 8px 0; color:#7a7a7a; font-size:15px; font-weight:bold;">🥈 PRATA (3 a 5 doações)</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Todos os benefícios do Bronze</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Desconto em eventos culturais</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Prioridade em vacinação</p>
            </div>
            <div style="background:#fffbe6; border-left:4px solid #ffd700; border-radius:10px; padding:15px 18px; margin:12px 0;">
                <p style="margin:0 0 8px 0; color:#b8860b; font-size:15px; font-weight:bold;">🥇 OURO (6 ou mais doações)</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Todos os benefícios do Prata</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Isenção em concursos do DF</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Meia-entrada em eventos culturais</p>
                <p style="margin:4px 0; color:#555; font-size:14px;">✅ Selo "Doador Ouro" no perfil</p>
            </div>
            <div style="text-align:center; margin:30px 0;">
                <a href="http://127.0.0.1:8000/beneficios/" style="display:inline-block; background:#b30000; color:#ffffff; padding:14px 32px; border-radius:50px; text-decoration:none; font-weight:bold; font-size:15px;">🎁 Ver meus benefícios</a>
            </div>
            <h3 style="color:#b30000; font-size:16px; margin-top:30px;">📋 Antes de ir, lembre-se:</h3>
            <ul style="color:#555; line-height:1.9; padding-left:20px; font-size:15px;">
                <li>Leve um documento com foto</li>
                <li>Chegue com 15 minutos de antecedência</li>
                <li>Beba bastante água antes</li>
                <li>Não vá em jejum</li>
                <li>Evite alimentos gordurosos</li>
            </ul>
            <p style="color:#888; font-size:14px; text-align:center; margin-top:35px; font-style:italic;">💗 Cada doação pode salvar até 4 vidas!</p>
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

Seu progresso: {total} doação(ões) — Nível {nivel} ({progresso}%)
{texto_falta}

Antes de ir:
- Leve documento com foto
- Chegue com 15 min de antecedência
- Beba bastante água
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

    assunto_hemocentro = f'🩸 Nova doação agendada - {doador.nome}'

    html_hemocentro = f'''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:Arial, sans-serif; background:#fcf9f2;">
    <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden;">
        <div style="background:linear-gradient(135deg, #b30000, #7a0000); padding:35px 30px; text-align:center; color:#fff;">
            <h1 style="margin:0; font-size:24px;">🩸 Nova Doação Agendada</h1>
            <p style="margin:10px 0 0 0; opacity:0.9; font-size:14px;">{agendamento.hemocentro.nome}</p>
        </div>
        <div style="padding:40px 30px;">
            <p style="color:#555; font-size:16px;">Olá, equipe! 👋</p>
            <p style="color:#555; font-size:16px;">Um novo doador agendou uma doação:</p>
            <div style="background:#fcf9f2; border-left:4px solid #b30000; padding:20px; border-radius:12px; margin:25px 0;">
                <p style="margin:8px 0; color:#333;"><strong>👤 Nome:</strong> {doador.nome}</p>
                <p style="margin:8px 0; color:#333;"><strong>🩸 Tipo sanguíneo:</strong> {doador.tipo_sanguineo}</p>
                <p style="margin:8px 0; color:#333;"><strong>📅 Data:</strong> {agendamento.data}</p>
                <p style="margin:8px 0; color:#333;"><strong>🕐 Horário:</strong> {agendamento.horario}</p>
                <p style="margin:8px 0; color:#333;"><strong>🩸 Tipo de doação:</strong> {agendamento.tipo_doacao}</p>
                <hr style="border:none; border-top:1px solid #e0e0e0; margin:18px 0;">
                <p style="margin:8px 0; color:#333;"><strong>📞 Telefone:</strong> {doador.telefone}</p>
                <p style="margin:8px 0; color:#333;"><strong>📧 E-mail:</strong> {doador.email}</p>
                <p style="margin:8px 0; color:#333;"><strong>{emoji} Nível:</strong> {nivel}</p>
            </div>
            <p style="color:#2e7d32; font-size:15px; text-align:center; padding:18px; background:#e8f5e9; border-radius:10px;">✅ <strong>Prepare o atendimento!</strong></p>
        </div>
        <div style="background:#7a0000; color:rgba(255,255,255,0.85); padding:25px; text-align:center; font-size:13px;">
            <p style="margin:0;">Sistema Sangue Bom 💗</p>
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
# E-MAIL DE DOAÇÃO REALIZADA
# =========================================================

def enviar_email_doacao_realizada(doador, agendamento):
    total = Agendamento.objects.filter(doador=doador, status='realizado').count()
    nivel, proximo, faltam, progresso, emoji = calcular_nivel(total)

    if doador.sexo == 'M':
        dias_espera = 60
        texto_sexo = 'Homens podem doar a cada 60 dias'
    elif doador.sexo == 'F':
        dias_espera = 90
        texto_sexo = 'Mulheres podem doar a cada 90 dias'
    else:
        dias_espera = 90
        texto_sexo = 'Recomendação padrão: 90 dias'

    data_base = agendamento.data
    if isinstance(data_base, str):
        data_base = datetime.strptime(data_base, '%Y-%m-%d').date()

    proxima_doacao = data_base + timedelta(days=dias_espera)
    data_exame = data_base + timedelta(days=9)

    proxima_doacao_fmt = proxima_doacao.strftime('%d/%m/%Y')
    data_exame_fmt = data_exame.strftime('%d/%m/%Y')

    if proximo:
        if faltam == 1:
            assunto = f'❤️ Obrigado por doar! Você está no {nivel} — Falta 1 pro {proximo} 🩸'
        else:
            assunto = f'❤️ Obrigado por doar! Você está no {nivel} — Faltam {faltam} pro {proximo} 🩸'
    else:
        assunto = f'🏆 Obrigado por doar! Você atingiu o nível OURO! 🩸'

    if proximo:
        msg_falta = f'Faltam <strong>{faltam} doações</strong> pro nível {proximo} {emoji}'
    else:
        msg_falta = '🏆 Você atingiu o <strong>nível máximo</strong>!'

    if nivel == 'Bronze':
        beneficios_html = '<p>✅ Certificado digital</p><p>✅ Acesso ao ranking</p>'
    elif nivel == 'Prata':
        beneficios_html = '<p>✅ Tudo do Bronze</p><p>✅ Desconto em eventos</p><p>✅ Prioridade em vacinação</p>'
    else:
        beneficios_html = '<p>✅ Tudo do Prata</p><p>✅ Isenção em concursos</p><p>✅ Meia-entrada</p><p>✅ Selo Ouro</p>'

    html = f'''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:Arial, sans-serif; background:#fcf9f2;">
    <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden;">
        <div style="background:linear-gradient(135deg, #b30000, #7a0000); padding:40px 30px; text-align:center; color:#fff;">
            <div style="font-size:60px;">❤️</div>
            <h1 style="margin:0; font-size:28px;">Obrigado por doar!</h1>
        </div>
        <div style="padding:40px 30px;">
            <h2 style="color:#b30000;">Olá, {doador.nome}! 👋</h2>
            <p style="color:#555; font-size:16px;">Sua doação no <strong>{agendamento.hemocentro.nome}</strong> foi confirmada!</p>
            <div style="background:#e8f5e9; border-left:4px solid #4caf50; padding:20px; border-radius:12px; margin:25px 0; text-align:center;">
                <p style="margin:0; color:#2e7d32; font-size:16px;">💗 <strong>Você salvou até 4 vidas!</strong></p>
            </div>
            <div style="background:#fff5f5; border:2px solid #b30000; border-radius:12px; padding:25px; margin:30px 0;">
                <h3 style="margin:0 0 15px 0; color:#b30000; text-align:center;">{emoji} Seu progresso</h3>
                <p style="text-align:center;">Você já fez <strong>{total} doação{'ões' if total != 1 else ''}</strong></p>
                <div style="background:#eee; border-radius:20px; height:24px; overflow:hidden; margin:15px 0;">
                    <div style="background:linear-gradient(90deg, #b30000, #ff6b6b); height:100%; width:{progresso}%;"></div>
                </div>
                <p style="text-align:center;"><strong>{progresso}%</strong> — Nível: <strong>{emoji} {nivel}</strong></p>
                <p style="text-align:center; color:#666;">{msg_falta}</p>
            </div>
            <div style="background:#f0f7ff; border-left:4px solid #1976d2; border-radius:12px; padding:20px; margin:25px 0;">
                <h3 style="margin:0 0 10px 0; color:#1565c0;">📅 Próxima doação</h3>
                <p style="text-align:center; color:#1565c0; font-size:22px; font-weight:bold;">{proxima_doacao_fmt}</p>
                <p style="text-align:center; font-style:italic; color:#666; font-size:13px;">({texto_sexo})</p>
            </div>
            <div style="background:#fff8e1; border-left:4px solid #ffc107; border-radius:12px; padding:20px; margin:25px 0;">
                <h3 style="margin:0 0 10px 0; color:#b8860b;">📋 Exame disponível</h3>
                <p style="text-align:center; color:#b8860b; font-size:22px; font-weight:bold;">{data_exame_fmt}</p>
                <p style="text-align:center; font-size:13px; color:#666;">Procure o {agendamento.hemocentro.nome}<br>📞 {agendamento.hemocentro.telefone}</p>
            </div>
            <h3 style="color:#b30000; text-align:center;">🎁 Seus benefícios — Nível {nivel}</h3>
            <div style="background:#fff5f5; border:2px solid #b30000; border-radius:12px; padding:20px; margin:20px 0;">
                {beneficios_html}
            </div>
            <div style="text-align:center; margin:30px 0;">
                <a href="http://127.0.0.1:8000/beneficios/" style="display:inline-block; background:#b30000; color:#fff; padding:14px 32px; border-radius:50px; text-decoration:none; font-weight:bold;">🎁 Ver meus benefícios</a>
            </div>
        </div>
        <div style="background:#7a0000; color:rgba(255,255,255,0.85); padding:25px; text-align:center; font-size:13px;">
            <p style="margin:0;">Sangue Bom 💗 — Doe sangue. Doe vida.</p>
        </div>
    </div>
</body>
</html>
'''

    texto = f'''Olá, {doador.nome}!

Sua doação no {agendamento.hemocentro.nome} foi confirmada! ❤️

Você acabou de salvar até 4 vidas!

Seu progresso: {total} doação(ões) — Nível {nivel} ({progresso}%)

PRÓXIMA DOAÇÃO: {proxima_doacao_fmt} ({texto_sexo})
EXAME: {data_exame_fmt}

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


# =========================================================
# E-MAIL DE PEDIDO APROVADO
# =========================================================

def enviar_email_pedido_aprovado(receptor, hemocentro):
    nome_responsavel = receptor.usuario.first_name if receptor.usuario else 'Responsável'
    email_responsavel = receptor.email_contato or (receptor.usuario.email if receptor.usuario else None)

    if not email_responsavel:
        print("Sem e-mail de contato.")
        return

    html = f'''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:Arial, sans-serif; background:#fcf9f2;">
    <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden;">
        <div style="background:linear-gradient(135deg, #b30000, #7a0000); padding:35px 30px; text-align:center; color:#fff;">
            <div style="font-size:50px;">✅</div>
            <h1 style="margin:0; font-size:26px;">Pedido Aprovado!</h1>
            <p style="margin:8px 0 0 0; font-size:14px;">{hemocentro.nome}</p>
        </div>
        <div style="padding:40px 30px;">
            <h2 style="color:#b30000;">Olá, {nome_responsavel}! 👋</h2>
            <p style="color:#555; font-size:16px;">O hemocentro <strong>{hemocentro.nome}</strong> <strong style="color:#2e7d32;">APROVOU</strong> o pedido para <strong>{receptor.nome}</strong>.</p>
            <div style="background:#e8f5e9; border-left:4px solid #4caf50; padding:20px; border-radius:12px; margin:25px 0;">
                <p style="margin:0; color:#2e7d32; font-size:16px;">💗 <strong>Estamos mobilizando doadores compatíveis!</strong></p>
                <p style="margin:8px 0 0 0; color:#555; font-size:14px;">Nossa equipe entrará em contato em breve.</p>
            </div>
            <h3 style="color:#b30000;">📋 Detalhes do Pedido:</h3>
            <div style="background:#fcf9f2; border-left:4px solid #b30000; padding:20px; border-radius:12px; margin:20px 0;">
                <p style="margin:8px 0;"><strong>👤 Paciente:</strong> {receptor.nome}</p>
                <p style="margin:8px 0;"><strong>🩸 Tipo sanguíneo:</strong> {receptor.tipo_sanguineo}</p>
                <p style="margin:8px 0;"><strong>💉 Tipo de doação:</strong> {receptor.get_tipo_doacao_display()}</p>
                <p style="margin:8px 0;"><strong>🏥 Hospital:</strong> {receptor.hospital}</p>
                <p style="margin:8px 0;"><strong>📍 Cidade:</strong> {receptor.cidade}</p>
                <p style="margin:8px 0;"><strong>📊 Urgência:</strong> {receptor.get_urgencia_display()}</p>
            </div>
            <h3 style="color:#b30000;">📞 Contato do Hemocentro:</h3>
            <div style="background:#f0f7ff; border-left:4px solid #1976d2; padding:20px; border-radius:12px; margin:20px 0;">
                <p style="margin:6px 0;"><strong>🏥 {hemocentro.nome}</strong></p>
                <p style="margin:6px 0;">📞 {hemocentro.telefone}</p>
                <p style="margin:6px 0;">📧 {hemocentro.email}</p>
                <p style="margin:6px 0;">📍 {hemocentro.endereco}, {hemocentro.bairro} - {hemocentro.cidade}</p>
            </div>
            <p style="text-align:center; color:#555;"><strong>Aguarde o nosso contato!</strong> 💗</p>
        </div>
        <div style="background:#7a0000; color:rgba(255,255,255,0.85); padding:25px; text-align:center; font-size:13px;">
            <p style="margin:0;">Sangue Bom 💗 — Este é um e-mail automático.</p>
        </div>
    </div>
</body>
</html>
'''

    texto = f'''Olá, {nome_responsavel}!

O hemocentro {hemocentro.nome} APROVOU o seu pedido para {receptor.nome}.

DETALHES:
- Paciente: {receptor.nome}
- Tipo sanguíneo: {receptor.tipo_sanguineo}
- Tipo de doação: {receptor.get_tipo_doacao_display}
- Hospital: {receptor.hospital}
- Cidade: {receptor.cidade}

Estamos mobilizando doadores. Entraremos em contato.

CONTATO:
{hemocentro.nome}
Tel: {hemocentro.telefone}
E-mail: {hemocentro.email}

Equipe Sangue Bom 💗
'''

    email = EmailMultiAlternatives(
        subject=f'✅ Pedido de doação aprovado - {receptor.nome}',
        body=texto,
        from_email=settings.EMAIL_HOST_USER,
        to=[email_responsavel]
    )
    email.attach_alternative(html, "text/html")
    email.send(fail_silently=False)


# =========================================================
# E-MAIL DE PEDIDO ATENDIDO
# =========================================================

def enviar_email_pedido_atendido(receptor, hemocentro):
    nome_responsavel = receptor.usuario.first_name if receptor.usuario else 'Responsável'
    email_responsavel = receptor.email_contato or (receptor.usuario.email if receptor.usuario else None)

    if not email_responsavel:
        print("Sem e-mail de contato.")
        return

    html = f'''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:Arial, sans-serif; background:#fcf9f2;">
    <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:16px; overflow:hidden;">
        <div style="background:linear-gradient(135deg, #1976d2, #0d47a1); padding:35px 30px; text-align:center; color:#fff;">
            <div style="font-size:50px;">🎉</div>
            <h1 style="margin:0; font-size:26px;">Sangue Disponível!</h1>
            <p style="margin:8px 0 0 0; font-size:14px;">{hemocentro.nome}</p>
        </div>
        <div style="padding:40px 30px;">
            <h2 style="color:#1976d2;">Olá, {nome_responsavel}! 👋</h2>
            <p style="color:#555; font-size:16px;">O hemocentro <strong>{hemocentro.nome}</strong> conseguiu mobilizar doadores e o estoque para <strong>{receptor.nome}</strong> está disponível! 🩸</p>
            <div style="background:#e3f2fd; border-left:4px solid #1976d2; padding:20px; border-radius:12px; margin:25px 0;">
                <p style="margin:0; color:#1565c0; font-size:16px;">✅ <strong>O que fazer agora?</strong></p>
                <p style="margin:10px 0 0 0; color:#555; font-size:14px;">Entre em contato com o <strong>hospital {receptor.hospital}</strong> para confirmar os próximos passos.</p>
            </div>
            <div style="background:#fff8e1; border-left:4px solid #ffc107; padding:20px; border-radius:12px; margin:25px 0;">
                <p style="margin:0; color:#856404; font-size:14px;">ℹ️ O sangue é processado e testado pelo hemocentro antes de ser liberado. O hospital é quem solicita a bolsa.</p>
            </div>
            <h3 style="color:#1976d2;">📋 Detalhes:</h3>
            <div style="background:#fcf9f2; border-left:4px solid #1976d2; padding:20px; border-radius:12px; margin:20px 0;">
                <p style="margin:8px 0;"><strong>👤 Paciente:</strong> {receptor.nome}</p>
                <p style="margin:8px 0;"><strong>🩸 Tipo sanguíneo:</strong> {receptor.tipo_sanguineo}</p>
                <p style="margin:8px 0;"><strong>💉 Tipo de doação:</strong> {receptor.get_tipo_doacao_display}</p>
                <p style="margin:8px 0;"><strong>🏥 Hospital:</strong> {receptor.hospital}</p>
                <p style="margin:8px 0;"><strong>📍 Cidade:</strong> {receptor.cidade}</p>
            </div>
            <h3 style="color:#1976d2;">📞 Contato do Hemocentro:</h3>
            <div style="background:#f0f7ff; border-left:4px solid #1976d2; padding:20px; border-radius:12px; margin:20px 0;">
                <p style="margin:6px 0;"><strong>🏥 {hemocentro.nome}</strong></p>
                <p style="margin:6px 0;">📞 {hemocentro.telefone}</p>
                <p style="margin:6px 0;">📧 {hemocentro.email}</p>
                <p style="margin:6px 0;">📍 {hemocentro.endereco}, {hemocentro.bairro} - {hemocentro.cidade}</p>
            </div>
            <p style="text-align:center; color:#555;"><strong>Entre em contato com o hospital para agendar o atendimento!</strong> 💗</p>
        </div>
        <div style="background:#0d47a1; color:rgba(255,255,255,0.85); padding:25px; text-align:center; font-size:13px;">
            <p style="margin:0;">Sangue Bom 💗 — Este é um e-mail automático.</p>
        </div>
    </div>
</body>
</html>
'''

    texto = f'''Olá, {nome_responsavel}!

SANGUE DISPONÍVEL! 🎉

O hemocentro {hemocentro.nome} conseguiu mobilizar doadores e o estoque para {receptor.nome} está disponível.

O QUE FAZER:
Entre em contato com o hospital {receptor.hospital}.

DETALHES:
- Paciente: {receptor.nome}
- Tipo sanguíneo: {receptor.tipo_sanguineo}
- Tipo de doação: {receptor.get_tipo_doacao_display}
- Hospital: {receptor.hospital}
- Cidade: {receptor.cidade}

CONTATO:
{hemocentro.nome}
Tel: {hemocentro.telefone}
E-mail: {hemocentro.email}

Equipe Sangue Bom 💗
'''

    email = EmailMultiAlternatives(
        subject=f'🎉 Sangue disponível - {receptor.nome}',
        body=texto,
        from_email=settings.EMAIL_HOST_USER,
        to=[email_responsavel]
    )
    email.attach_alternative(html, "text/html")
    email.send(fail_silently=False)