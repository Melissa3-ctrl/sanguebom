from .models import Doador, Notificacao


def notificacoes_nao_lidas(request):
    if request.user.is_authenticated:
        try:
            doador = Doador.objects.get(usuario=request.user)
            total = Notificacao.objects.filter(doador=doador, lida=False).count()
            return {'notificacoes_nao_lidas': total}
        except Doador.DoesNotExist:
            return {'notificacoes_nao_lidas': 0}
    return {'notificacoes_nao_lidas': 0}