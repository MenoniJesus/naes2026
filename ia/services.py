"""Única porta de entrada para a IA no projeto.

Nenhum outro módulo deve importar o SDK `anthropic`: toda chamada passa por
`chamar_ia`, que confere se a IA está ativa, a permissão e a cota do usuário,
chama a API e grava a auditoria em `RequisicaoIA` (inclusive erros e bloqueios).
"""
import time
from dataclasses import dataclass

import anthropic
from django.conf import settings

from .models import ConfiguracaoIA, CotaUsuarioIA, RequisicaoIA

# Em recusas por segurança a API repete o pedido em outro modelo dentro da mesma chamada.
BETA_FALLBACK = "server-side-fallback-2026-07-01"

AVISO_RECUSA = "Não posso ajudar com esse pedido. Tente reformular a pergunta."
AVISO_CORTE = "\n\n_(Resposta interrompida pelo limite de tokens.)_"


class ErroIA(Exception):
    """Erro com mensagem pronta para mostrar ao usuário."""

    def __init__(self, mensagem, requisicao=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.requisicao = requisicao


class IAIndisponivel(ErroIA):
    """IA desativada, sem chave ou com falha na API."""


class AcessoNegado(ErroIA):
    """Usuário sem permissão ou sem cota."""


@dataclass
class RespostaIA:
    texto: str
    tokens_entrada: int
    tokens_saida: int
    duracao_ms: int
    requisicao: RequisicaoIA
    recusada: bool = False

    @property
    def tokens_total(self) -> int:
        return self.tokens_entrada + self.tokens_saida


# ─────────────────────────────────────────
# COTA
# ─────────────────────────────────────────

def consumo_do_mes(usuario) -> int:
    return RequisicaoIA.objects.filter(user=usuario).do_mes().tokens_consumidos()


def situacao_do_usuario(usuario, configuracao=None) -> dict:
    """Permissão, cota e consumo do mês corrente, para as telas e para `chamar_ia`."""
    configuracao = configuracao or ConfiguracaoIA.carregar()
    cota_usuario = CotaUsuarioIA.objects.filter(user=usuario).first()

    habilitado = cota_usuario.habilitado if cota_usuario else True
    cota = cota_usuario.cota_efetiva(configuracao) if cota_usuario else configuracao.cota_mensal_padrao
    consumo = consumo_do_mes(usuario)

    return {
        "habilitado": habilitado,
        "cota": cota,
        "consumo": consumo,
        "restante": max(cota - consumo, 0),
        "percentual": min(round(consumo * 100 / cota), 100) if cota else 100,
    }


# ─────────────────────────────────────────
# CHAMADA
# ─────────────────────────────────────────

def chamar_ia(*, usuario, mensagens, sistema="", origem="geral", aplicar_limites=True, max_tokens=None):
    """Envia `mensagens` (lista de {"role", "content"}) à IA e devolve um `RespostaIA`.

    Lança `AcessoNegado` (sem permissão/cota) ou `IAIndisponivel` (desativada, sem
    chave ou erro na API). Toda tentativa fica registrada em `RequisicaoIA`.
    `aplicar_limites=False` ignora ativação, permissão e cota (usado no “Testar conexão”).
    """
    configuracao = ConfiguracaoIA.carregar()
    auditoria = {
        "user": usuario if getattr(usuario, "is_authenticated", False) else None,
        "origem": origem,
        "modelo": configuracao.modelo,
        "pergunta": _ultima_pergunta(mensagens),
        "mensagens_enviadas": len(mensagens),
    }

    if aplicar_limites:
        if not configuracao.ativo:
            _recusar(auditoria, IAIndisponivel, "A IA está desativada no momento.")
        situacao = situacao_do_usuario(usuario, configuracao)
        if not situacao["habilitado"]:
            _recusar(auditoria, AcessoNegado, "Seu usuário não tem permissão para usar a IA.")
        if situacao["restante"] <= 0:
            _recusar(
                auditoria, AcessoNegado,
                f"Sua cota mensal de {situacao['cota']:,} tokens acabou. "
                "Ela é renovada no início do próximo mês.".replace(",", "."),
            )

    chave = configuracao.api_key or settings.ANTHROPIC_API_KEY
    if not chave:
        _recusar(
            auditoria, IAIndisponivel,
            "Nenhuma chave de API configurada. Informe-a na tela de configuração da IA.",
            status="erro",
        )

    parametros = {
        "model": configuracao.modelo,
        "max_tokens": max_tokens or configuracao.max_tokens,
        "messages": mensagens,
    }
    if sistema:
        parametros["system"] = sistema
    if configuracao.esforco:
        parametros["output_config"] = {"effort": configuracao.esforco}
    if configuracao.usar_fallback:
        parametros["betas"] = [BETA_FALLBACK]
        parametros["fallbacks"] = "default"

    inicio = time.monotonic()
    try:
        cliente = anthropic.Anthropic(
            api_key=chave,
            timeout=configuracao.timeout_segundos,
            max_retries=2,
        )
        resposta = cliente.beta.messages.create(**parametros)
    except anthropic.AnthropicError as erro:
        auditoria["duracao_ms"] = _ms_desde(inicio)
        _recusar(auditoria, IAIndisponivel, _mensagem_de_erro(erro, configuracao.modelo),
                 status="erro", detalhe=repr(erro))

    duracao_ms = _ms_desde(inicio)
    texto = "".join(bloco.text for bloco in resposta.content if bloco.type == "text").strip()
    recusada = resposta.stop_reason == "refusal"
    if recusada:
        texto = texto or AVISO_RECUSA
    elif resposta.stop_reason == "max_tokens":
        texto += AVISO_CORTE

    uso = resposta.usage
    tokens_entrada = (
        (uso.input_tokens or 0)
        + (getattr(uso, "cache_read_input_tokens", 0) or 0)
        + (getattr(uso, "cache_creation_input_tokens", 0) or 0)
    )
    tokens_saida = uso.output_tokens or 0

    # Com fallback, `resposta.model` é o modelo que de fato respondeu.
    auditoria["modelo"] = resposta.model or configuracao.modelo
    requisicao = RequisicaoIA.objects.create(
        **auditoria,
        resposta=texto,
        tokens_entrada=tokens_entrada,
        tokens_saida=tokens_saida,
        duracao_ms=duracao_ms,
        status="recusada" if recusada else "sucesso",
        id_requisicao_api=getattr(resposta, "_request_id", None) or "",
    )

    return RespostaIA(
        texto=texto,
        tokens_entrada=tokens_entrada,
        tokens_saida=tokens_saida,
        duracao_ms=duracao_ms,
        requisicao=requisicao,
        recusada=recusada,
    )


def testar_conexao(usuario):
    """Chamada mínima para validar chave e modelo, ignorando ativação e cota."""
    return chamar_ia(
        usuario=usuario,
        mensagens=[{"role": "user", "content": "Responda apenas com a palavra OK."}],
        origem="teste_conexao",
        aplicar_limites=False,
        max_tokens=512,
    )


# ─────────────────────────────────────────
# AUXILIARES
# ─────────────────────────────────────────

def _ultima_pergunta(mensagens) -> str:
    for mensagem in reversed(mensagens):
        if mensagem.get("role") == "user":
            conteudo = mensagem.get("content", "")
            return conteudo if isinstance(conteudo, str) else str(conteudo)
    return ""


def _ms_desde(inicio) -> int:
    return int((time.monotonic() - inicio) * 1000)


def _recusar(auditoria, classe_erro, mensagem, status="bloqueada", detalhe=""):
    requisicao = RequisicaoIA.objects.create(**auditoria, status=status, erro=detalhe or mensagem)
    raise classe_erro(mensagem, requisicao=requisicao)


def _mensagem_de_erro(erro, modelo) -> str:
    # Do mais específico para o mais genérico: as classes do SDK herdam umas das outras.
    if isinstance(erro, anthropic.AuthenticationError):
        return "A chave da API é inválida."
    if isinstance(erro, anthropic.PermissionDeniedError):
        return "A chave da API não tem permissão para usar este modelo."
    if isinstance(erro, anthropic.NotFoundError):
        return f"O modelo “{modelo}” não foi encontrado."
    if isinstance(erro, anthropic.RateLimitError):
        return "Limite de requisições da API atingido. Tente novamente em instantes."
    if isinstance(erro, anthropic.BadRequestError):
        return f"A API recusou a requisição: {erro.message}"
    if isinstance(erro, anthropic.APIStatusError):
        return f"A API da IA respondeu com erro {erro.status_code}. Tente novamente mais tarde."
    if isinstance(erro, anthropic.APITimeoutError):
        return "A IA demorou demais para responder. Tente novamente."
    if isinstance(erro, anthropic.APIConnectionError):
        return "Não foi possível conectar à API da IA."
    return "Erro inesperado ao chamar a IA."
