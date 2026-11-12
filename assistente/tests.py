from unittest import mock

import anthropic
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ia.models import RequisicaoIA
from ia.tests import mock_cliente, resposta_falsa

from .models import MensagemAssistente
from .services import JANELA_MENSAGENS, instrucoes_do_sistema, montar_janela
from .templatetags.markdown_seguro import renderizar_markdown


class JanelaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="senha-forte-123")

    def test_envia_so_as_ultimas_mensagens_comecando_pelo_usuario(self):
        for i in range(6):
            MensagemAssistente.objects.create(user=self.usuario, papel="user", conteudo=f"pergunta {i}")
            MensagemAssistente.objects.create(user=self.usuario, papel="assistant", conteudo=f"resposta {i}")

        janela = montar_janela(self.usuario, "nova")

        self.assertLessEqual(len(janela), JANELA_MENSAGENS)
        self.assertEqual(janela[0]["role"], "user")
        self.assertEqual(janela[-1], {"role": "user", "content": "nova"})
        self.assertEqual(janela[-2]["content"], "resposta 5")
        self.assertNotIn("pergunta 0", [m["content"] for m in janela])

    def test_nao_mistura_historico_de_outro_usuario(self):
        outro = User.objects.create_user("bia", password="senha-forte-123")
        MensagemAssistente.objects.create(user=outro, papel="user", conteudo="segredo da bia")

        janela = montar_janela(self.usuario, "oi")

        self.assertEqual(janela, [{"role": "user", "content": "oi"}])

    def test_instrucoes_incluem_o_contexto_do_projeto(self):
        instrucoes = instrucoes_do_sistema()
        self.assertIn("<contexto_do_sistema>", instrucoes)
        self.assertIn("SobraNada", instrucoes)
        self.assertIn("Responda apenas sobre o SobraNada", instrucoes)


class MarkdownTests(TestCase):
    def test_renderiza_markdown(self):
        html = renderizar_markdown("**Cadastrar** → Produto\n\n1. um\n2. dois")
        self.assertIn("<strong>Cadastrar</strong>", html)
        self.assertIn("<ol>", html)

    def test_remove_html_perigoso(self):
        html = renderizar_markdown(
            '<script>alert(1)</script> <img src=x onerror="alert(2)"> [link](javascript:alert(3))'
        )
        self.assertNotIn("<script", html)
        self.assertNotIn("onerror", html)
        self.assertNotIn("<img", html)
        self.assertNotIn("javascript:", html)


@override_settings(ANTHROPIC_API_KEY="chave-de-teste")
class AssistenteViewTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="senha-forte-123")
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.usuario)

    def tearDown(self):
        mock.patch.stopall()

    def csrf_token(self):
        self.client.get(reverse("assistente"))
        return self.client.cookies["csrftoken"].value

    def test_pagina_renderiza(self):
        resposta = self.client.get(reverse("assistente"))
        self.assertContains(resposta, "Assistente SobraNada")

    def test_ajax_sem_csrf_e_recusado(self):
        mock_cliente()
        resposta = self.client.post(reverse("assistente-perguntar"), {"pergunta": "Oi"})
        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(MensagemAssistente.objects.exists())

    def test_ajax_com_csrf_responde_e_grava_historico(self):
        mock_cliente(resposta_falsa("Use o menu **Cadastrar**. <script>x()</script>"))

        resposta = self.client.post(
            reverse("assistente-perguntar"), {"pergunta": "Como cadastro?"},
            HTTP_X_CSRFTOKEN=self.csrf_token(),
        )

        self.assertEqual(resposta.status_code, 200)
        dados = resposta.json()
        self.assertIn("<strong>Cadastrar</strong>", dados["html"])
        self.assertNotIn("<script", dados["html"])
        self.assertEqual(dados["situacao"]["consumo"], 15)
        self.assertEqual(
            list(MensagemAssistente.objects.values_list("papel", flat=True)), ["user", "assistant"]
        )
        self.assertEqual(RequisicaoIA.objects.get().origem, "assistente")

    def test_pergunta_vazia(self):
        resposta = self.client.post(
            reverse("assistente-perguntar"), {"pergunta": "   "}, HTTP_X_CSRFTOKEN=self.csrf_token(),
        )
        self.assertEqual(resposta.status_code, 400)

    def test_falha_da_ia_nao_grava_historico(self):
        mock_cliente(erro=anthropic.AnthropicError("falhou"))

        resposta = self.client.post(
            reverse("assistente-perguntar"), {"pergunta": "Oi"}, HTTP_X_CSRFTOKEN=self.csrf_token(),
        )

        self.assertEqual(resposta.status_code, 503)
        self.assertIn("erro", resposta.json())
        self.assertFalse(MensagemAssistente.objects.exists())
        self.assertEqual(RequisicaoIA.objects.get().status, "erro")

    def test_limpar_historico(self):
        MensagemAssistente.objects.create(user=self.usuario, papel="user", conteudo="oi")
        outro = User.objects.create_user("bia", password="senha-forte-123")
        MensagemAssistente.objects.create(user=outro, papel="user", conteudo="oi")

        self.client.post(reverse("assistente-limpar"), HTTP_X_CSRFTOKEN=self.csrf_token())

        self.assertFalse(MensagemAssistente.objects.filter(user=self.usuario).exists())
        self.assertTrue(MensagemAssistente.objects.filter(user=outro).exists())
