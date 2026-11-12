# AGENTS.md: SobraNada

Instruções para agentes de IA (Claude Code, Codex, Copilot etc.) que trabalham neste repositório.

## O projeto

SobraNada é um sistema Django para reduzir o desperdício de alimentos: estabelecimentos
vendem com desconto **sacolas** com as sobras do dia, e clientes as **reservam** para retirar.
O contexto funcional completo (regras, descontos, fluxos) está em
[assistente/contexto_projeto.md](assistente/contexto_projeto.md). Leia-o antes de mexer em
regras de negócio.

## Stack

- Python 3.12+ (GAE `python312`; local com `uv`), Django 5.2, PostgreSQL (Neon)
- django-filter, django-crispy-forms (Bootstrap 5), django-braces, django-debug-toolbar
- Front: Bootstrap 5 + jQuery com os plugins DataTables, Bootbox e jQuery Mask (CDN em `website/templates/website/modelo2.html`)
- IA: SDK oficial `anthropic` (modelo padrão `claude-opus-5-5`), Markdown com `markdown` + sanitização com `nh3`
- Deploy: Google App Engine (`app.yaml`), estáticos em `static_gcloud/`

## Estrutura

| Pasta | O que tem |
|---|---|
| `DjangoProject/` | settings, urls raiz, wsgi |
| `website/` | landing page, painel (`hub`), login/registro, layout base `modelo2.html` |
| `sobraNada/` | domínio: models, CRUDs (CBVs), filtros, carrinho, `precificacao.py` (desconto, sem Django) |
| `ia/` | **única porta de entrada para a IA**: configuração, cotas, auditoria e as telas de gestão |
| `assistente/` | chat com a IA: histórico por usuário, janela de 5 mensagens, AJAX, Markdown sanitizado |
| `.agents/skills/` | skills dos agentes (`.claude/skills` aponta para cá) |

## Comandos

```bash
uv sync                                   # instala dependências (inclui dev)
.venv/bin/python manage.py runserver      # roda local (usa o .env)
.venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate

# Testes: rode SEMPRE em SQLite, para não criar banco de teste no Neon
DATABASE_URL=sqlite:///test_local.sqlite3 .venv/bin/pytest -q
```

## Convenções de código

- **Português** em nomes de classes, variáveis, mensagens e comentários (`Sacola`, `reservar`, `campo_dono`).
  Campos de model antigos em inglês (`name`, `price`) ficam como estão.
- CRUD com **class-based views** e os mixins de `sobraNada/views.py`:
  - `BaseLoginMixin`: exige login
  - `DonoMixin` (`campo_dono`): restringe o queryset ao dono, e registro de outro usuário vira 404
  - `MensagemMixin`: mensagem de sucesso em cadastro, alteração e exclusão; trata `ProtectedError`
  - `GroupRequiredMixin` (`group_required = ['admin']`) ou `ia.permissoes.AdminRequiredMixin` para telas de admin
- Formulários usam o template genérico `sobraNada/form.html` com `titulo`/`botao` em `extra_context`.
- Listagens: classe `table-datatable` (DataTables), filtro com django-filter e
  `{% include "sobraNada/includes/pagination.html" %}`, cuja templatetag `pagination_query` preserva os filtros.
- **Sem N+1**: toda listagem que mostra FK ou `__str__` que acessa relação usa `select_related` /
  `prefetch_related` (ex.: `Sacola.__str__` usa os produtos e o estabelecimento). Há teste em
  `sobraNada/tests/test_views.py::QueriesTests` que falha se a contagem de queries crescer com as linhas.
- Toda ação de cadastro/alteração/exclusão dá feedback com `django.contrib.messages`.
- Rotas nomeadas `<modelo>-<acao>` (`sacola-create`, `reserva-list`); no app ia, `ia-<tela>`.

## Regras da IA (obrigatórias)

1. **Nunca** importe `anthropic` fora de `ia/services.py`. Qualquer funcionalidade com IA chama
   `ia.services.chamar_ia(usuario=..., mensagens=..., sistema=..., origem="<nome>")`.
2. `chamar_ia` já confere ativação, permissão, cota mensal e grava a auditoria (`RequisicaoIA`).
   Não duplique essas regras; trate `AcessoNegado` e `IAIndisponivel` (ambos `ErroIA`, com `.mensagem`).
3. Texto vindo da IA só vai para o HTML pelo filtro `markdown_seguro` (sanitizado com nh3).
4. Testes nunca chamam a API real: use `ia.tests.mock_cliente(...)`.

## Segurança

- Nunca faça commit do `.env` nem de chaves. A chave da IA vem de `ANTHROPIC_API_KEY` ou da tela
  IA › Configuração, e nunca é exibida de volta.
- Endpoints AJAX são POST com CSRF (`X-CSRFToken`); não use `csrf_exempt`.

## Skills disponíveis

| Skill | Quando usar |
|---|---|
| [mensagem-commit](.agents/skills/mensagem-commit/SKILL.md) | Ao criar qualquer commit |
| [novo-crud](.agents/skills/novo-crud/SKILL.md) | Ao criar um model novo com telas de CRUD |
| [funcionalidade-ia](.agents/skills/funcionalidade-ia/SKILL.md) | Ao criar algo que usa IA |
| [deploy-gae](.agents/skills/deploy-gae/SKILL.md) | Ao publicar no Google App Engine |
