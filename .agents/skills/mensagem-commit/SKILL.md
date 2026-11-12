---
name: mensagem-commit
description: Padroniza as mensagens de commit do SobraNada (Conventional Commits em português). Use sempre que for criar um commit, sugerir uma mensagem de commit ou revisar mensagens de commit.
---

# Mensagens de commit

## Formato

```
<tipo>(<escopo>): <descrição>

<corpo opcional: o porquê da mudança, em até 72 colunas por linha>

<rodapé opcional: Refs #12, BREAKING CHANGE: ...>
```

- **descrição**: português, letra minúscula, verbo no presente do indicativo na 3ª pessoa
  ("adiciona", "corrige", "remove"), sem ponto final, até 72 caracteres no total da linha.
- **escopo** (opcional): o app ou a área afetada: `sobraNada`, `ia`, `assistente`, `website`,
  `deploy`, `agentes`. Omita quando a mudança atravessa vários apps.

## Tipos

| Tipo | Quando |
|---|---|
| `feat` | funcionalidade nova para o usuário |
| `fix` | correção de bug |
| `perf` | melhora de desempenho (ex.: remover N+1 com `select_related`) |
| `refactor` | muda o código sem mudar o comportamento |
| `test` | só testes |
| `docs` | só documentação (`AGENTS.md`, `contexto_projeto.md`, skills) |
| `style` | só templates/CSS, sem mudar lógica |
| `chore` | dependências, configuração, build, deploy |
| `checkpoint` | entrega parcial de uma avaliação (já usado no histórico) |

## Passo a passo

1. Rode `git status` e `git diff --staged` e entenda o que mudou.
2. Confira que **nenhum** `.env`, `*.sqlite3` ou chave de API está no stage. Se estiver, pare e avise.
3. Se o diff mistura assuntos sem relação (ex.: correção de bug + funcionalidade nova), sugira
   dividir em mais de um commit.
4. Escolha o tipo pelo efeito principal da mudança, não pelo arquivo.
5. Escreva a descrição dizendo **o que** muda; use o corpo para o **porquê** quando não for óbvio.
6. Termine com as linhas de atribuição que o ambiente pedir (ex.: `Co-Authored-By:`).

## Exemplos

```
feat(ia): adiciona tela de configuração com teste de conexão
fix(sobraNada): impede excluir reserva já avaliada
perf(sobraNada): remove N+1 na listagem de reservas

Sacola.__str__ acessa produtos e estabelecimento; sem o prefetch cada
linha fazia duas queries extras.
chore(deploy): força HTTPS e DEBUG=False no app.yaml
docs(agentes): cria AGENTS.md e skills do projeto
```

Evite: `ajustes`, `update`, `wip`, `corrigindo coisas`, mensagens em inglês ou com ponto final.
