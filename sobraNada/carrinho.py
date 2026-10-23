from decimal import Decimal

from . import precificacao
from .models import Produto

SESSION_KEY = "carrinho"


class Carrinho:
    """Carrinho de produtos guardado na sessão do usuário."""

    def __init__(self, request):
        self.session = request.session
        self.dados = self.session.setdefault(SESSION_KEY, {})

    def adicionar(self, produto: Produto, quantidade: int = 1):
        produto_id = str(produto.pk)
        self.dados[produto_id] = self.dados.get(produto_id, 0) + quantidade
        self._salvar()

    def atualizar(self, produto_id, quantidade: int):
        produto_id = str(produto_id)
        if produto_id not in self.dados:
            return
        if quantidade < 1:
            self.remover(produto_id)
            return
        self.dados[produto_id] = quantidade
        self._salvar()

    def remover(self, produto_id):
        produto_id = str(produto_id)
        if produto_id in self.dados:
            del self.dados[produto_id]
            self._salvar()

    def limpar(self):
        self.dados = {}
        self._salvar()

    def _salvar(self):
        self.session[SESSION_KEY] = self.dados
        self.session.modified = True

    def __len__(self):
        return sum(self.dados.values())

    def itens(self):
        produtos = Produto.objects.filter(pk__in=self.dados.keys()).select_related("estabelecimento")
        itens = []
        for produto in produtos:
            quantidade = self.dados[str(produto.pk)]
            itens.append({
                "produto": produto,
                "quantidade": quantidade,
                "subtotal": produto.price * quantidade,
            })
        return itens

    def calcular(self):
        itens = self.itens()
        subtotal = sum((item["subtotal"] for item in itens), Decimal("0.00"))
        desconto = precificacao.calcular_desconto_carrinho(subtotal)
        return itens, desconto
