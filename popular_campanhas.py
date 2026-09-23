from django.core.management.base import BaseCommand
from membros.models import Campanha


class Command(BaseCommand):
    help = 'Popula o banco com campanhas pré-definidas'

    def handle(self, *args, **kwargs):
        # APAGA tudo antes de criar
        Campanha.objects.all().delete()
        self.stdout.write('🗑️  Campanhas antigas deletadas.')

        campanhas = [
            {
                'emoji': '🩸',
                'titulo': 'Doe Sangue, Salve Vidas',
                'descricao': 'Campanha permanente de incentivo à doação de sangue. Qualquer tipo sanguíneo é bem-vindo. Venha contribuir!',
                'status': 'ativa',
                'local': 'Fundação Hemocentro de Brasília',
                'data': 'Durante todo o ano',
            },
            {
                'emoji': '💗',
                'titulo': 'Doe com Quem Você Ama',
                'descricao': 'Incentive alguém especial a participar da doação de sangue e transforme esse momento em uma atitude de solidariedade.',
                'status': 'breve',
                'local': 'Taguatinga e Gama',
                'data': 'Próxima campanha',
            },
            {
                'emoji': '🌟',
                'titulo': 'Doador Nota 10',
                'descricao': 'Valorize sua participação na doação de sangue e incentive outros doadores a fazerem parte dessa corrente do bem.',
                'status': 'ativa',
                'local': 'Locais de atendimento participantes',
                'data': 'Durante o ano',
            },
            {
                'emoji': '🚨',
                'titulo': 'Doe Quando o Estoque Estiver Crítico',
                'descricao': 'Alguns tipos sanguíneos podem entrar em situação crítica. Sua doação pode ajudar a reforçar os estoques e atender quem precisa.',
                'status': 'urgente',
                'local': 'Fundação Hemocentro de Brasília',
                'data': 'Enquanto houver necessidade',
            },
            {
                'emoji': '🎓',
                'titulo': 'Doe Sangue, Compartilhe Solidariedade',
                'descricao': 'Uma campanha de conscientização para incentivar jovens e estudantes a conhecerem a importância da doação de sangue.',
                'status': 'ativa',
                'local': 'Brasília, Taguatinga e Gama',
                'data': 'Durante o ano',
            },
            {
                'emoji': '👶',
                'titulo': 'Sangue para Quem Precisa',
                'descricao': 'Crianças, adultos e pacientes em situações delicadas podem precisar de transfusões. Cada doação faz parte dessa corrente de cuidado.',
                'status': 'ativa',
                'local': 'Locais de atendimento participantes',
                'data': 'Contínua',
            },
            {
                'emoji': '🎄',
                'titulo': 'Natal Solidário',
                'descricao': 'Doe sangue neste Natal e dê o presente mais valioso: a vida. Uma ação especial de fim de ano para reforçar os estoques nos feriados.',
                'status': 'breve',
                'local': 'Fundação Hemocentro de Brasília',
                'data': 'Dezembro',
            },
            {
                'emoji': '👨‍👩‍👧',
                'titulo': 'Doe em Família',
                'descricao': 'Traga sua família para doar junto. Uma ação que fortalece laços e salva vidas. Cada membro pode fazer a diferença.',
                'status': 'ativa',
                'local': 'Taguatinga',
                'data': 'Todo primeiro sábado do mês',
            },
            {
                'emoji': '🏃',
                'titulo': 'Corrida pela Vida',
                'descricao': 'Participe da nossa corrida solidária e doe sangue no mesmo dia. Esporte e solidariedade juntos pela vida.',
                'status': 'breve',
                'local': 'Parque da Cidade',
                'data': 'Outubro',
            },
            {
                'emoji': '🎸',
                'titulo': 'Rock pela Vida',
                'descricao': 'Shows e doação de sangue no mesmo evento. Traga um amigo, doe, e curta boa música. Uma ação para o público jovem.',
                'status': 'ativa',
                'local': 'Conic',
                'data': 'Último domingo do mês',
            },
            {
                'emoji': '🎁',
                'titulo': 'Doe e Ganhe Benefícios',
                'descricao': 'Doe sangue e desbloqueie benefícios exclusivos como descontos em eventos culturais, prioridade em vacinação e muito mais.',
                'status': 'ativa',
                'local': 'Todos os hemocentros parceiros',
                'data': 'Contínua',
            },
            {
                'emoji': '🩺',
                'titulo': 'Semana da Doação',
                'descricao': 'Uma semana inteira dedicada à doação de sangue com programação especial, palestras e atendimento estendido.',
                'status': 'breve',
                'local': 'Fundação Hemocentro de Brasília',
                'data': '14 a 20 de novembro',
            },
        ]

        for c in campanhas:
            Campanha.objects.create(ativa=True, **c)
            self.stdout.write(f'✅ {c["emoji"]} {c["titulo"]}')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 {len(campanhas)} campanhas criadas!'))
        self.stdout.write(f'📊 Total no banco: {Campanha.objects.count()}')