from types import SimpleNamespace
from unittest import mock

import anthropic
import httpx2
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ConfiguracaoIA, CotaUsuarioIA, RequisicaoIA
from . import services
from .services import AcessoNegado, IAIndisponivel, chamar_ia, situacao_do_usuario

MENSAGENS = [{"role": "user", "content": "Olá"}]


def resposta_falsa(texto="Resposta", stop_reason="end_turn", entrada=10, saida=5):
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=texto)],
        stop_reason=stop_reason,
        model="claude-opus-5-5",
        usage=SimpleNamespace(
            input_tokens=entrada, output_tokens=saida,
            cache_read_input_tokens=0, cache_creation_input_tokens=0,
        ),
        _request_id="req_teste",
    )


def mock_cliente(resposta=None, erro=None):
    """Substitui anthropic.Anthropic dentro de ia.services."""
    patcher = mock.patch("ia.services.anthropic.Anthropic")
    classe = patcher.start()
    criar = classe.return_value.beta.messages.create
    if erro is not None:
        criar.side_effect = erro
    else:
        criar.return_value = resposta or resposta_falsa()
    return patcher, criar


@override_settings(ANTHROPIC_API_KEY="chave-de-teste")
class ChamarIATests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="senha-forte-123")

    def tearDown(self):
        mock.patch.stopall()

    def test_sucesso_registra_auditoria_com_tokens(self):
        _, criar = mock_cliente(resposta_falsa("Oi!", entrada=120, saida=30))

        resposta = chamar_ia(usuario=self.usuario, mensagens=MENSAGENS, sistema="Regras", origem="teste")

        self.assertEqual(resposta.texto, "Oi!")
        requisicao = RequisicaoIA.objects.get()
        self.assertEqual(requisicao.status, "sucesso")
        self.assertEqual(requisicao.tokens_total, 150)
        self.assertEqual(requisicao.user, self.usuario)
        self.assertEqual(requisicao.pergunta, "Olá")
        self.assertEqual(requisicao.id_requisicao_api, "req_teste")

        parametros = criar.call_args.kwargs
        self.assertEqual(parametros["model"], "claude-opus-5-5")
        self.assertEqual(parametros["system"], "Regras")
        self.assertEqual(parametros["output_config"], {"effort": "low"})
        self.assertEqual(parametros["fallbacks"], "default")

    def test_cota_esgotada_bloqueia_sem_chamar_a_api(self):
        _, criar = mock_cliente()
        CotaUsuarioIA.objects.create(user=self.usuario, cota_mensal=100)
        RequisicaoIA.objects.create(user=self.usuario, origem="x", modelo="m", pergunta="p",
                                    status="sucesso", tokens_entrada=80, tokens_saida=20)

        with self.assertRaises(AcessoNegado):
            chamar_ia(usuario=self.usuario, mensagens=MENSAGENS)

        criar.assert_not_called()
        self.assertEqual(RequisicaoIA.objects.filter(status="bloqueada").count(), 1)

    def test_usuario_desabilitado_e_bloqueado(self):
        _, criar = mock_cliente()
        CotaUsuarioIA.objects.create(user=self.usuario, habilitado=False)

        with self.assertRaises(AcessoNegado):
            chamar_ia(usuario=self.usuario, mensagens=MENSAGENS)
        criar.assert_not_called()

    def test_ia_desativada(self):
        mock_cliente()
        configuracao = ConfiguracaoIA.carregar()
        configuracao.ativo = False
        configuracao.save()

        with self.assertRaises(IAIndisponivel):
            chamar_ia(usuario=self.usuario, mensagens=MENSAGENS)

    @override_settings(ANTHROPIC_API_KEY="")
    def test_sem_chave_configurada(self):
        _, criar = mock_cliente()

        with self.assertRaises(IAIndisponivel) as contexto:
            chamar_ia(usuario=self.usuario, mensagens=MENSAGENS)

        self.assertIn("chave", contexto.exception.mensagem)
        criar.assert_not_called()

    def test_erro_de_conexao_vira_mensagem_amigavel_e_fica_auditado(self):
        erro = anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com"))
        mock_cliente(erro=erro)

        with self.assertRaises(IAIndisponivel) as contexto:
            chamar_ia(usuario=self.usuario, mensagens=MENSAGENS)

        self.assertEqual(contexto.exception.mensagem, "Não foi possível conectar à API da IA.")
        self.assertEqual(RequisicaoIA.objects.get().status, "erro")

    def test_recusa_do_modelo(self):
        mock_cliente(resposta_falsa("", stop_reason="refusal"))

        resposta = chamar_ia(usuario=self.usuario, mensagens=MENSAGENS)

        self.assertTrue(resposta.recusada)
        self.assertTrue(resposta.texto)
        self.assertEqual(RequisicaoIA.objects.get().status, "recusada")

    def test_sem_fallback_e_sem_esforco(self):
        _, criar = mock_cliente()
        configuracao = ConfiguracaoIA.carregar()
        configuracao.usar_fallback = False
        configuracao.esforco = ""
        configuracao.save()

        chamar_ia(usuario=self.usuario, mensagens=MENSAGENS)

        parametros = criar.call_args.kwargs
        self.assertNotIn("fallbacks", parametros)
        self.assertNotIn("output_config", parametros)

    def test_testar_conexao_ignora_ativacao_e_cota(self):
        mock_cliente()
        configuracao = ConfiguracaoIA.carregar()
        configuracao.ativo = False
        configuracao.save()
        CotaUsuarioIA.objects.create(user=self.usuario, habilitado=False)

        resposta = services.testar_conexao(self.usuario)

        self.assertEqual(resposta.requisicao.origem, "teste_conexao")

    def test_situacao_usa_cota_padrao_e_soma_o_mes(self):
        RequisicaoIA.objects.create(user=self.usuario, origem="x", modelo="m", pergunta="p",
                                    status="sucesso", tokens_entrada=600, tokens_saida=400)

        situacao = situacao_do_usuario(self.usuario)

        self.assertEqual(situacao["cota"], 100_000)
        self.assertEqual(situacao["consumo"], 1000)
        self.assertEqual(situacao["percentual"], 1)


@override_settings(ANTHROPIC_API_KEY="chave-de-teste")
class TelasIATests(TestCase):
    def setUp(self):
        self.comum = User.objects.create_user("comum", password="senha-forte-123")
        self.admin = User.objects.create_user("gestor", password="senha-forte-123")
        self.admin.groups.add(Group.objects.get_or_create(name="admin")[0])

    def tearDown(self):
        mock.patch.stopall()

    def test_telas_de_gestao_sao_so_para_admin(self):
        self.client.force_login(self.comum)
        for rota in ["ia-requisicao-list", "ia-configuracao", "ia-usuario-list"]:
            resposta = self.client.get(reverse(rota))
            self.assertRedirects(resposta, reverse("hub"), fetch_redirect_response=False)

        self.client.force_login(self.admin)
        for rota in ["ia-requisicao-list", "ia-configuracao", "ia-usuario-list"]:
            self.assertEqual(self.client.get(reverse(rota)).status_code, 200)

    def test_meu_consumo_mostra_so_as_proprias_requisicoes(self):
        RequisicaoIA.objects.create(user=self.comum, origem="x", modelo="m", pergunta="minha pergunta", status="sucesso")
        RequisicaoIA.objects.create(user=self.admin, origem="x", modelo="m", pergunta="pergunta alheia", status="sucesso")
        self.client.force_login(self.comum)

        resposta = self.client.get(reverse("ia-meu-consumo"))

        self.assertContains(resposta, "minha pergunta")
        self.assertNotContains(resposta, "pergunta alheia")

    def test_salvar_configuracao_mantem_chave_quando_em_branco(self):
        configuracao = ConfiguracaoIA.carregar()
        configuracao.api_key = "sk-ant-antiga-1234"
        configuracao.save()
        self.client.force_login(self.admin)

        resposta = self.client.post(reverse("ia-configuracao"), {
            "ativo": "on", "modelo": "claude-sonnet-5-5", "api_key": "", "max_tokens": 1024,
            "esforco": "medium", "usar_fallback": "on", "timeout_segundos": 30, "cota_mensal_padrao": 5000,
        })

        self.assertRedirects(resposta, reverse("ia-configuracao"))
        configuracao.refresh_from_db()
        self.assertEqual(configuracao.modelo, "claude-sonnet-5-5")
        self.assertEqual(configuracao.api_key, "sk-ant-antiga-1234")
        self.assertEqual(configuracao.atualizado_por, self.admin)
        self.assertNotContains(self.client.get(reverse("ia-configuracao")), "sk-ant-antiga-1234")

    def test_botao_testar_conexao(self):
        mock_cliente()
        self.client.force_login(self.admin)

        resposta = self.client.post(reverse("ia-configuracao-testar"), follow=True)

        self.assertContains(resposta, "Conexão OK")
        self.assertEqual(RequisicaoIA.objects.get().origem, "teste_conexao")

    def test_editar_cota_de_um_usuario(self):
        self.client.force_login(self.admin)

        resposta = self.client.post(
            reverse("ia-usuario-update", args=[self.comum.pk]),
            {"habilitado": "", "cota_mensal": 500, "observacao": "Testes"},
        )

        self.assertRedirects(resposta, reverse("ia-usuario-list"))
        cota = CotaUsuarioIA.objects.get(user=self.comum)
        self.assertFalse(cota.habilitado)
        self.assertEqual(cota.cota_mensal, 500)
