from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from ia.services import AcessoNegado, ErroIA, situacao_do_usuario

from .models import MensagemAssistente
from .services import JANELA_MENSAGENS, TAMANHO_MAXIMO_PERGUNTA, perguntar

SUGESTOES = [
    "Como começo a vender minhas sobras no SobraNada?",
    "Como funciona o desconto de uma reserva?",
    "Como cancelo uma reserva?",
    "Quando posso avaliar uma reserva?",
]


@login_required
def assistente(request):
    return render(request, 'assistente/assistente.html', {
        'historico': MensagemAssistente.objects.filter(user=request.user),
        'situacao': situacao_do_usuario(request.user),
        'janela': JANELA_MENSAGENS,
        'tamanho_maximo': TAMANHO_MAXIMO_PERGUNTA,
        'sugestoes': SUGESTOES,
    })


@login_required
@require_POST
def assistente_perguntar(request):
    """Endpoint AJAX: recebe `pergunta` e devolve o HTML das duas mensagens novas.

    O CSRF é validado pelo CsrfViewMiddleware (cabeçalho X-CSRFToken enviado pelo JS).
    """
    pergunta = request.POST.get('pergunta', '').strip()
    if not pergunta:
        return JsonResponse({'erro': 'Digite uma pergunta.'}, status=400)
    if len(pergunta) > TAMANHO_MAXIMO_PERGUNTA:
        return JsonResponse(
            {'erro': f'A pergunta pode ter no máximo {TAMANHO_MAXIMO_PERGUNTA} caracteres.'},
            status=400,
        )

    try:
        mensagem_usuario, mensagem_assistente, _ = perguntar(request.user, pergunta)
    except AcessoNegado as erro:
        return JsonResponse({'erro': erro.mensagem}, status=403)
    except ErroIA as erro:
        return JsonResponse({'erro': erro.mensagem}, status=503)

    html = render_to_string('assistente/_mensagem.html', {'mensagem': mensagem_usuario}, request=request)
    html += render_to_string('assistente/_mensagem.html', {'mensagem': mensagem_assistente}, request=request)
    return JsonResponse({
        'html': html,
        'situacao': situacao_do_usuario(request.user),
    })


@login_required
@require_POST
def assistente_limpar(request):
    apagadas, _ = MensagemAssistente.objects.filter(user=request.user).delete()
    if apagadas:
        messages.success(request, "Histórico da conversa apagado.")
    else:
        messages.info(request, "Não havia mensagens para apagar.")
    return redirect('assistente')
