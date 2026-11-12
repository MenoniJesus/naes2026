---
name: deploy-gae
description: Publica o SobraNada no Google App Engine com checagens antes e depois (testes, requirements, estáticos, migrações, deploy e verificação da URL). Use quando pedirem para fazer deploy, publicar ou atualizar o site no GAE.
---

# Deploy no Google App Engine

Projeto GCP: confira com `gcloud config get-value project`. URL: `gcloud app browse --no-launch-browser`.

O deploy muda o site público: **confirme com o usuário antes do passo 6**.

## Passos

1. **Testes** (SQLite, nunca o banco real):
   ```bash
   DATABASE_URL=sqlite:///test_local.sqlite3 .venv/bin/pytest -q && rm -f test_local.sqlite3
   ```
   Pare se algum falhar.
2. **Checagem de produção**:
   ```bash
   DEBUG=False .venv/bin/python manage.py check --deploy
   ```
3. **Dependências**: o GAE instala pelo `requirements.txt`, não pelo `pyproject.toml`.
   ```bash
   uv export --no-hashes --format requirements-txt --no-dev -o requirements.txt
   ```
4. **Estáticos**: o GAE serve `static_gcloud/` direto (handler `/static` no `app.yaml`).
   ```bash
   .venv/bin/python manage.py collectstatic --noinput
   ```
5. **Migrações** no banco de produção (o mesmo `DATABASE_URL` do `.env`):
   ```bash
   .venv/bin/python manage.py migrate
   ```
6. **Deploy**:
   ```bash
   gcloud app deploy app.yaml --quiet
   ```
7. **Verificação**: abra a URL e confira `/`, `/login/` e, logado, `/hub/` e `/assistente/`.
   Erros: `gcloud app logs tail -s default`.

## Pontos de atenção

- O `.env` **é enviado** no deploy (não está no `.gcloudignore`) porque guarda `SECRET_KEY`,
  `DATABASE_URL` e `ANTHROPIC_API_KEY`. O `app.yaml` força `DEBUG=False`, que tem prioridade
  sobre o `.env`.
- `.venv/`, `.git`, `.idea/`, `.agents/` e `.claude/` ficam fora do upload (`.gcloudignore`).
- Atrás do proxy do GAE o Django precisa de `SECURE_PROXY_SSL_HEADER` (já em `settings.py`
  quando `DEBUG=False`), senão os POSTs falham no CSRF.
- Sem `ANTHROPIC_API_KEY` o site funciona, mas a IA responde "Nenhuma chave de API configurada"
  até alguém salvar a chave em IA › Configuração.
