import datetime
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.contrib.messages import get_messages
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from sobraNada.models import (
    Categoria, Cidade, Endereco, Estabelecimento, Estado, Notificacao, Produto, Reserva, Sacola,
)


def textos_das_mensagens(resposta):
    return [str(m) for m in get_messages(resposta.wsgi_request)]


class Base(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana", password="senha-forte-123")
        self.bia = User.objects.create_user("bia", password="senha-forte-123")
        self.estado = Estado.objects.create(name="Paraná", uf="PR")
        self.cidade = Cidade.objects.create(estado=self.estado, name="Curitiba")
        self.endereco = Endereco.objects.create(
            cidade=self.cidade, street="Rua XV", number="10", neighborhood="Centro", zip_code="80000-000",
        )
        self.categoria = Categoria.objects.create(name="Padaria")
        self.loja_ana = self.criar_loja(self.ana, "Padaria da Ana")

    def criar_loja(self, usuario, nome):
        return Estabelecimento.objects.create(
            user=usuario, endereco=self.endereco, categoria=self.categoria, name=nome,
            pickup_start=datetime.time(17), pickup_end=datetime.time(19),
        )

    def criar_sacola(self, loja, titulo="Sacola surpresa"):
        produto = Produto.objects.create(estabelecimento=loja, name=f"Pão {titulo}", price=Decimal("30.00"))
        sacola = Sacola.objects.create(
            title=titulo, original_price=Decimal("30.00"), sale_price=Decimal("15.00"),
            total_quantity=5, available_quantity=5, expiry_date=timezone.localdate(),
            pickup_start=datetime.time(17), pickup_end=datetime.time(19),
        )
        sacola.produtos.add(produto)
        return sacola


class MensagensTests(Base):
    def test_cadastro_alteracao_e_exclusao_exibem_mensagem(self):
        self.client.force_login(self.ana)

        resposta = self.client.post(reverse("cidade-create"), {"estado": self.estado.pk, "name": "Londrina"})
        self.assertIn('Registro de cidade "Londrina - PR" cadastrado com sucesso.', textos_das_mensagens(resposta))

        cidade = Cidade.objects.get(name="Londrina")
        resposta = self.client.post(reverse("cidade-update", args=[cidade.pk]), {"estado": self.estado.pk, "name": "Maringá"})
        self.assertIn('Alterações em cidade "Maringá - PR" salvas com sucesso.', textos_das_mensagens(resposta))

        resposta = self.client.post(reverse("cidade-delete", args=[cidade.pk]))
        self.assertIn('Registro de cidade "Maringá - PR" excluído com sucesso.', textos_das_mensagens(resposta))

    def test_exclusao_protegida_vira_mensagem_de_erro(self):
        admin = User.objects.create_user("gestor", password="senha-forte-123")
        admin.groups.add(Group.objects.get_or_create(name="admin")[0])
        self.client.force_login(admin)

        resposta = self.client.post(reverse("estado-delete", args=[self.estado.pk]), follow=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(Estado.objects.filter(pk=self.estado.pk).exists())
        self.assertContains(resposta, "existem outros registros vinculados")


class DonoTests(Base):
    def test_produto_e_criado_no_estabelecimento_do_usuario(self):
        self.client.force_login(self.ana)
        self.client.post(reverse("produto-create"), {"name": "Bolo", "price": "20.00", "is_active": "on"})
        self.assertEqual(Produto.objects.get(name="Bolo").estabelecimento, self.loja_ana)

    def test_sem_estabelecimento_redireciona_para_cadastrar(self):
        self.client.force_login(self.bia)
        resposta = self.client.get(reverse("produto-create"))
        self.assertRedirects(resposta, reverse("estabelecimento-create"))

    def test_outro_usuario_nao_altera_nem_exclui_produto_ou_sacola(self):
        sacola = self.criar_sacola(self.loja_ana)
        produto = sacola.produtos.get()
        self.client.force_login(self.bia)

        self.assertEqual(self.client.get(reverse("produto-update", args=[produto.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("produto-delete", args=[produto.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("sacola-update", args=[sacola.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("sacola-delete", args=[sacola.pk])).status_code, 404)

    def test_dono_edita_sacola_com_varios_produtos(self):
        sacola = self.criar_sacola(self.loja_ana)
        sacola.produtos.add(Produto.objects.create(estabelecimento=self.loja_ana, name="Broa", price=Decimal("5")))
        self.client.force_login(self.ana)
        self.assertEqual(self.client.get(reverse("sacola-update", args=[sacola.pk])).status_code, 200)

    def test_notificacoes_so_do_proprio_usuario(self):
        propria = Notificacao.objects.create(user=self.ana, title="Minha", message="m")
        alheia = Notificacao.objects.create(user=self.bia, title="Alheia", message="m")
        self.client.force_login(self.ana)

        lista = self.client.get(reverse("notificacao-list"))
        self.assertContains(lista, "Minha")
        self.assertNotContains(lista, "Alheia")
        self.assertEqual(self.client.get(reverse("notificacao-detail", args=[propria.pk])).status_code, 200)
        for rota in ["notificacao-detail", "notificacao-update", "notificacao-delete"]:
            self.assertEqual(self.client.get(reverse(rota, args=[alheia.pk])).status_code, 404)


class QueriesTests(Base):
    """A quantidade de queries das listagens não pode crescer com o número de linhas."""

    def contar_queries(self, rota):
        with CaptureQueriesContext(connection) as contexto:
            resposta = self.client.get(reverse(rota))
        self.assertEqual(resposta.status_code, 200)
        return len(contexto)

    def test_listagens_sem_n_mais_1(self):
        self.client.force_login(self.ana)
        loja_bia = self.criar_loja(self.bia, "Mercado da Bia")
        self.criar_sacola(self.loja_ana, "A")
        Reserva.objects.create(user=self.ana, sacola=self.criar_sacola(loja_bia, "B"), quantity=1)

        rotas = ["endereco-list", "reserva-list", "sacola-list", "produto-list", "avaliacao-list", "hub"]
        antes = {rota: self.contar_queries(rota) for rota in rotas}

        for i in range(4):
            cidade = Cidade.objects.create(estado=self.estado, name=f"Cidade {i}")
            Endereco.objects.create(cidade=cidade, street="Rua", number=str(i), neighborhood="B", zip_code="1")
            sacola = self.criar_sacola(loja_bia, f"Extra {i}")
            Reserva.objects.create(user=self.ana, sacola=sacola, quantity=1)

        depois = {rota: self.contar_queries(rota) for rota in rotas}
        self.assertEqual(antes, depois)
