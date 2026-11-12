# SobraNada: contexto do sistema

O SobraNada é uma plataforma web contra o desperdício de alimentos. Estabelecimentos
(padarias, mercados, restaurantes) vendem com desconto as **sacolas** com produtos que
sobraram no dia, e os clientes **reservam** essas sacolas para retirar no local, dentro do
horário de retirada.

## Perfis de uso

- **Cliente**: qualquer usuário cadastrado. Navega pelas sacolas e produtos, faz reservas,
  usa o carrinho, avalia reservas retiradas e consulta as próprias notificações.
- **Lojista**: usuário que cadastrou um **estabelecimento** (no máximo um por usuário).
  Cadastra produtos e monta sacolas apenas com os próprios produtos, e vê as reservas
  feitas nas suas sacolas.
- **Administrador** (grupo "admin" ou superusuário): cadastra estados e categorias e
  gerencia a IA (requisições, configuração e cota de cada usuário).

## Cadastros e regras

- **Estado, Cidade, Endereço**: localização. Endereço tem rua, número, complemento, bairro e CEP.
- **Perfil**: dados extras do usuário (telefone e endereço). Um por usuário.
- **Categoria**: tipo de estabelecimento (ex.: Padaria). Só administradores cadastram.
- **Estabelecimento**: nome, categoria, endereço, foto, horário de retirada e se está ativo.
  Um por usuário. Só o dono altera ou exclui.
- **Produto**: nome, descrição, preço e se está ativo. Sempre pertence ao estabelecimento
  do usuário que o cadastrou; só o dono altera ou exclui.
- **Sacola**: reúne produtos de um mesmo estabelecimento. O **preço original** é a soma dos
  produtos, e o **preço de venda** precisa ser menor que ele. Tem quantidade total, quantidade
  disponível, validade (não pode estar no passado), horário de retirada e status
  (disponível, esgotada, expirada). Quando a quantidade disponível chega a zero, a sacola fica
  esgotada.
- **Reserva**: o cliente escolhe uma sacola disponível e a quantidade. Recebe um **código de
  retirada** de 8 caracteres. Status: pendente, confirmada, retirada ou cancelada. Ao cancelar,
  as unidades voltam para o estoque da sacola. Só reservas pendentes ou confirmadas podem ter a
  quantidade alterada ou ser canceladas. Reservas já avaliadas não podem ser excluídas.
- **Avaliação**: nota de 1 a 5 e comentário, apenas para reservas com status "retirada" do
  próprio usuário, uma por reserva.
- **Notificação**: avisos do usuário (reserva, lembrete, promoção, sistema). Cada usuário só vê as
  próprias. Ao fazer uma reserva, o sistema cria uma notificação com o valor e o código.

## Descontos

**Na reserva**, sobre o total (preço da sacola × quantidade):

| Total da reserva | Desconto |
|---|---|
| até R$ 100,00 | 0% |
| R$ 100,01 a R$ 250,00 | 10% |
| R$ 250,01 a R$ 500,00 | 20% |
| R$ 500,01 a R$ 1.000,00 | 25% |
| acima de R$ 1.000,00 | 30% |

**No carrinho de produtos**, sobre o total do carrinho:

| Total do carrinho | Desconto |
|---|---|
| até R$ 149,99 | 0% |
| R$ 150,00 a R$ 249,99 | 20% |
| R$ 250,00 a R$ 499,99 | 25% |
| a partir de R$ 500,00 | 35% |

## Navegação

- **Painel**: página inicial depois do login, com atalhos para todos os cadastros e as
  sacolas e reservas recentes.
- **Cadastrar** (menu superior): formulários de cada cadastro.
- **Listar** (menu superior): listagens com busca, ordenação e paginação. Produtos, Sacolas e
  Reservas têm filtros (por nome/título, estabelecimento, status...).
- **Carrinho**: na lista de produtos, o botão com o ícone de carrinho adiciona o produto.
- **IA** (menu superior): Assistente, Meu consumo e, para administradores, Requisições,
  IA por usuário e Configuração.

## Fluxos comuns

1. **Começar a vender**: Cadastrar → Estabelecimento → depois Cadastrar → Produto → depois
   Cadastrar → Sacola (escolhendo os produtos).
2. **Reservar**: Listar → Sacolas → ver detalhes → botão "Reservar" (ou Cadastrar → Reserva).
   O desconto aparece no valor total da reserva.
3. **Cancelar uma reserva**: Listar → Reservas → botão de cancelar (ícone octógono) na linha.
4. **Avaliar**: depois que a reserva estiver como "retirada", Cadastrar → Avaliação.
5. **Alterar senha**: pelo endereço /mudar-senha/.

## Assistente de IA

O assistente responde dúvidas sobre o uso do sistema. Ele não acessa os dados do banco e não
executa ações. Cada pergunta consome tokens da cota mensal do usuário (ver "Meu consumo").
O assistente só recebe as últimas 5 mensagens da conversa como contexto.
