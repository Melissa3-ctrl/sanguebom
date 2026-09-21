from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from .models import Doador, Hemocentro, Agendamento, Notificacao


# =========================================================
# TESTES DE PÁGINAS BÁSICAS
# =========================================================

class PaginasTest(TestCase):

    def test_home_abre(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_beneficios_abre(self):
        response = self.client.get('/beneficios/')
        self.assertEqual(response.status_code, 200)

    def test_duvidas_abre(self):
        response = self.client.get('/duvidas/')
        self.assertEqual(response.status_code, 200)

    def test_login_abre(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_tipos_sanguineos_abre(self):
        response = self.client.get('/tipos_sanguineos/')
        self.assertEqual(response.status_code, 200)

    def test_quero_doar_abre(self):
        response = self.client.get('/quero_doar/')
        self.assertEqual(response.status_code, 200)

    def test_locais_para_doar_abre(self):
        response = self.client.get('/locais_para_doar/')
        self.assertEqual(response.status_code, 200)


# =========================================================
# TESTES DE LOGIN
# =========================================================

class LoginTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='joao@email.com',
            email='joao@email.com',
            password='senha12345'
        )
        Doador.objects.create(
            usuario=self.user,
            nome='João',
            email='joao@email.com',
            telefone='61999999999',
            tipo_sanguineo='O+',
            data_nascimento='1990-01-01'
        )

    def test_login_correto(self):
        response = self.client.post('/login/', {
            'email': 'joao@email.com',
            'senha': 'senha12345'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_errado(self):
        response = self.client.post('/login/', {
            'email': 'joao@email.com',
            'senha': 'senha_errada'
        })
        self.assertEqual(response.status_code, 200)


# =========================================================
# TESTES DE DOADOR
# =========================================================

class DoadorTest(TestCase):

    def test_criar_doador(self):
        user = User.objects.create_user(
            username='maria@email.com',
            password='senha12345'
        )
        doador = Doador.objects.create(
            usuario=user,
            nome='Maria',
            email='maria@email.com',
            telefone='61888888888',
            tipo_sanguineo='A+',
            data_nascimento='1995-05-05'
        )
        self.assertEqual(doador.nome, 'Maria')
        self.assertEqual(Doador.objects.count(), 1)

    def test_total_doadores(self):
        User.objects.create_user(username='a@a.com', password='12345678')
        User.objects.create_user(username='b@b.com', password='12345678')
        self.assertEqual(User.objects.count(), 2)


# =========================================================
# TESTES DE HEMOCENTRO
# =========================================================

class HemocentroTest(TestCase):

    def setUp(self):
        # Cria user do hemocentro
        self.user_hemo = User.objects.create_user(
            username='taguatinga@teste.com',
            password='senha12345'
        )
        # Cria hemocentro
        self.hemocentro = Hemocentro.objects.create(
            usuario=self.user_hemo,
            nome='Taguatinga',
            endereco='Área Especial',
            bairro='Taguatinga',
            cidade='Brasília',
            cep='72000-000',
            telefone='6133334444',
            email='tag@teste.com',
            horario_abertura='08:00',
            horario_fechamento='18:00',
            dias_atendimento='Seg-Sex',
            ativo=True
        )

    def test_hemocentro_criado(self):
        self.assertEqual(self.hemocentro.nome, 'Taguatinga')
        self.assertEqual(self.hemocentro.usuario.username, 'taguatinga@teste.com')

    def test_hemocentro_tem_usuario(self):
        self.assertEqual(self.hemocentro.usuario, self.user_hemo)

    def test_painel_hemocentro_logado(self):
        self.client.login(username='taguatinga@teste.com', password='senha12345')
        response = self.client.get('/painel/')
        self.assertEqual(response.status_code, 200)

    def test_painel_hemocentro_deslogado(self):
        response = self.client.get('/painel/')
        self.assertEqual(response.status_code, 302)


# =========================================================
# TESTES DE ADMIN
# =========================================================

class AdminTest(TestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin@teste.com',
            email='admin@teste.com',
            password='admin12345'
        )

    def test_admin_acessa_relatorios(self):
        self.client.login(username='admin@teste.com', password='admin12345')
        response = self.client.get('/relatorios/')
        self.assertEqual(response.status_code, 200)

    def test_admin_nao_acessa_notificacoes(self):
        self.client.login(username='admin@teste.com', password='admin12345')
        response = self.client.get('/notificacoes/')
        # Redireciona pro relatórios
        self.assertEqual(response.status_code, 302)

    def test_admin_nao_acessa_painel(self):
        self.client.login(username='admin@teste.com', password='admin12345')
        response = self.client.get('/painel/')
        # Redireciona
        self.assertEqual(response.status_code, 302)


# =========================================================
# TESTES DE AGENDAMENTO
# =========================================================

class AgendamentoTest(TestCase):

    def setUp(self):
        # Doador
        self.user_doador = User.objects.create_user(
            username='doador@teste.com',
            password='senha12345'
        )
        self.doador = Doador.objects.create(
            usuario=self.user_doador,
            nome='Doador Teste',
            email='doador@teste.com',
            telefone='61999999999',
            tipo_sanguineo='O+',
            data_nascimento='1990-01-01'
        )

        # Hemocentro
        self.user_hemo = User.objects.create_user(
            username='hemo@teste.com',
            password='senha12345'
        )
        self.hemocentro = Hemocentro.objects.create(
            usuario=self.user_hemo,
            nome='Hemocentro Teste',
            endereco='Endereço',
            bairro='Bairro',
            cidade='Brasília',
            cep='72000-000',
            telefone='6133334444',
            email='hemo@teste.com',
            horario_abertura='08:00',
            horario_fechamento='18:00',
            dias_atendimento='Seg-Sex',
            ativo=True
        )

    def test_agendar_logado(self):
        self.client.login(username='doador@teste.com', password='senha12345')

        response = self.client.post('/agendar_doacao/', {
            'hemocentro': self.hemocentro.id,
            'data': '2026-10-01',
            'horario': '10:00',
            'tipo_doacao': 'Sangue total'
        })

        # Cria o agendamento
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_agendar_cria_notificacao(self):
        self.client.login(username='doador@teste.com', password='senha12345')

        self.client.post('/agendar_doacao/', {
            'hemocentro': self.hemocentro.id,
            'data': '2026-10-01',
            'horario': '10:00',
            'tipo_doacao': 'Sangue total'
        })

        # Cria notificação
        self.assertEqual(Notificacao.objects.count(), 2)  # confirmado + nivel

    def test_agendar_deslogado(self):
        response = self.client.post('/agendar_doacao/', {})
        # Redireciona pro login
        self.assertEqual(response.status_code, 302)


# =========================================================
# TESTES DE NOTIFICAÇÕES
# =========================================================

class NotificacaoTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='notif@teste.com',
            password='senha12345'
        )
        self.doador = Doador.objects.create(
            usuario=self.user,
            nome='Notif',
            email='notif@teste.com',
            telefone='61999999999',
            tipo_sanguineo='A+',
            data_nascimento='1990-01-01'
        )

    def test_notificacoes_deslogado(self):
        response = self.client.get('/notificacoes/')
        self.assertEqual(response.status_code, 302)

    def test_criar_notificacao(self):
        Notificacao.objects.create(
            doador=self.doador,
            tipo='alerta',
            titulo='Teste',
            mensagem='Mensagem de teste'
        )
        self.assertEqual(Notificacao.objects.count(), 1)

    def test_marcar_lida(self):
        notif = Notificacao.objects.create(
            doador=self.doador,
            tipo='alerta',
            titulo='Teste',
            mensagem='Mensagem'
        )
        self.client.login(username='notif@teste.com', password='senha12345')
        self.client.get(f'/notificacoes/{notif.id}/lida/')

        notif.refresh_from_db()
        self.assertTrue(notif.lida)