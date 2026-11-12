---
name: funcionalidade-ia
description: Como criar ou alterar qualquer funcionalidade que usa IA no SobraNada, sempre pela porta única ia.services.chamar_ia (cota, permissão e auditoria), com saída sanitizada e testes com cliente simulado. Use ao mexer nos apps ia ou assistente ou ao adicionar um recurso com IA.
---

# Funcionalidade com IA

## Regra de ouro

Só `ia/services.py` importa o SDK `anthropic`. Tudo o mais chama:

```python
from ia.services import AcessoNegado, ErroIA, chamar_ia

resposta = chamar_ia(
    usuario=request.user,
    mensagens=[{"role": "user", "content": texto}],  # a conversa deve começar por "user"
    sistema=INSTRUCOES,          # instruções fixas: deixe-as estáveis (sem data/hora)
    origem="resumo_reserva",     # identifica a funcionalidade na auditoria
)
resposta.texto, resposta.tokens_total, resposta.recusada, resposta.requisicao
```

`chamar_ia` já faz: checa se a IA está ativa, se o usuário está habilitado e tem cota no mês,
chama a API com o modelo/esforço/fallback da configuração, e grava `RequisicaoIA` em **todas** as
tentativas (sucesso, erro, recusa, bloqueio). Não reimplemente nada disso.

## Passo a passo

1. Escolha um `origem` novo e curto (snake_case). Ele aparece no filtro da tela de Requisições.
2. Escreva as instruções do sistema em português, com **limites explícitos** (o que pode e o que
   não pode responder) e o formato esperado. Veja `assistente/services.py::INSTRUCOES`.
   Se precisar de contexto do sistema, leia `assistente/contexto_projeto.md`; não copie o texto.
3. Trate os erros na view:
   - `AcessoNegado` (sem permissão/cota) → HTTP 403 ou `messages.error`
   - `ErroIA` (inclui `IAIndisponivel`) → HTTP 503 ou `messages.error`
   - sempre mostre `erro.mensagem`, que já é amigável.
4. Saída para o HTML: **sempre** `{% load markdown_seguro %}{{ texto|markdown_seguro }}`. Nunca use
   `|safe` em texto vindo da IA.
5. Se for AJAX: `@login_required` + `@require_POST`, CSRF via cabeçalho `X-CSRFToken`, resposta
   `JsonResponse`. Nunca use `csrf_exempt`.
6. Se guardar conversa, envie só uma janela das últimas mensagens (veja `montar_janela`).
7. Se mudar o contexto funcional do sistema, atualize `assistente/contexto_projeto.md`.

## Testes

Nunca chame a API real. Use o helper:

```python
from ia.tests import mock_cliente, resposta_falsa

def test_algo(self):
    _, criar = mock_cliente(resposta_falsa("texto", entrada=10, saida=5))
    ...
    criar.call_args.kwargs["system"]  # confira o que foi enviado
```

Cubra: sucesso grava auditoria com a `origem` certa, `AcessoNegado` quando a cota acaba e saída
sem `<script>`. Rode com `DATABASE_URL=sqlite:///test_local.sqlite3 .venv/bin/pytest -q`.

## Configuração (tela IA › Configuração)

Modelo (padrão `claude-opus-5-5`), chave (ou `ANTHROPIC_API_KEY`), máximo de tokens, esforço,
fallback em recusas, timeout e cota mensal padrão. O botão **Testar conexão** valida chave e
modelo sem consumir a cota.
