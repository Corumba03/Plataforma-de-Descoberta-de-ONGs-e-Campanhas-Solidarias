"""Testes unitários para as rotas da aplicação."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

from werkzeug.exceptions import NotFound

from app.models import AreaAtuacao, Campanha, ContatoOng, Noticia, Ong


def _mock_ong(**kwargs):
    """Cria um objeto mock que simula uma instância de Ong."""
    area = MagicMock(spec=AreaAtuacao)
    area.nome_area = kwargs.pop("area", "Educação")

    ong = MagicMock(spec=Ong)
    ong.id = kwargs.pop("id", uuid.uuid4())
    ong.nome = kwargs.pop("nome", "ONG Teste")
    ong.descricao = kwargs.pop("descricao", "Descrição padrão.")
    ong.cnpj = kwargs.pop("cnpj", "12345678000199")
    ong.area_atuacao = area
    ong.contatos = kwargs.pop("contatos", [])
    ong.campanhas = kwargs.pop("campanhas", [])
    ong.noticias = kwargs.pop("noticias", [])
    return ong


def _mock_contato(**kw):
    c = MagicMock(spec=ContatoOng)
    c.tipo_contato = kw.get("tipo", "Email")
    c.valor = kw.get("valor", "contato@ong.org")
    return c


def _mock_campanha(**kw):
    c = MagicMock(spec=Campanha)
    c.titulo = kw.get("titulo", "Campanha")
    c.status = kw.get("status", "ativa")
    return c


def _mock_noticia(**kw):
    n = MagicMock(spec=Noticia)
    n.titulo = kw.get("titulo", "Notícia")
    n.link = kw.get("link", None)
    n.data_publicacao = kw.get("data", datetime(2026, 4, 1))
    return n

class TestIndex:

    def test_retorna_200_html(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.content_type

class TestHealth:

    def test_retorna_json_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.get_json() == {"status": "ok"}

class TestOngProfile:

    @patch("app.main.routes.db.get_or_404")
    def test_ong_existente(self, mock_get, client):
        ong = _mock_ong(nome="Alpha", cnpj="99887766000155", area="Meio Ambiente")
        mock_get.return_value = ong

        r = client.get(f"/ong/{ong.id}")

        assert r.status_code == 200
        mock_get.assert_called_once_with(Ong, ong.id)
        assert b"Alpha" in r.data
        assert b"99887766000155" in r.data
        assert "Meio Ambiente".encode() in r.data

    @patch("app.main.routes.db.get_or_404")
    def test_ong_inexistente(self, mock_get, client):
        mock_get.side_effect = NotFound()
        r = client.get(f"/ong/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_id_invalido(self, client):
        r = client.get("/ong/nao-e-uuid")
        assert r.status_code == 404

    @patch("app.main.routes.db.get_or_404")
    def test_exibe_contatos(self, mock_get, client):
        ong = _mock_ong(contatos=[_mock_contato(valor="x@y.org")])
        mock_get.return_value = ong

        r = client.get(f"/ong/{ong.id}")
        assert b"x@y.org" in r.data

    @patch("app.main.routes.db.get_or_404")
    def test_sem_contatos(self, mock_get, client):
        mock_get.return_value = _mock_ong(contatos=[])
        ong_id = mock_get.return_value.id

        r = client.get(f"/ong/{ong_id}")
        assert "Nenhum contato cadastrado".encode() in r.data

    @patch("app.main.routes.db.get_or_404")
    def test_exibe_campanhas(self, mock_get, client):
        ong = _mock_ong(campanhas=[_mock_campanha(titulo="Camp Visível")])
        mock_get.return_value = ong

        r = client.get(f"/ong/{ong.id}")
        assert "Camp Visível".encode() in r.data

    @patch("app.main.routes.db.get_or_404")
    def test_sem_campanhas(self, mock_get, client):
        mock_get.return_value = _mock_ong(campanhas=[])
        r = client.get(f"/ong/{mock_get.return_value.id}")
        assert "Nenhuma campanha no momento".encode() in r.data

    @patch("app.main.routes.db.get_or_404")
    def test_exibe_noticias_com_link(self, mock_get, client):
        n = _mock_noticia(titulo="Nova", link="https://ex.org/n")
        mock_get.return_value = _mock_ong(noticias=[n])

        r = client.get(f"/ong/{mock_get.return_value.id}")
        assert b"Nova" in r.data
        assert b"https://ex.org/n" in r.data
        assert b"<a " in r.data

    @patch("app.main.routes.db.get_or_404")
    def test_sem_noticias(self, mock_get, client):
        mock_get.return_value = _mock_ong(noticias=[])
        r = client.get(f"/ong/{mock_get.return_value.id}")
        assert "Nenhuma notícia recente".encode() in r.data

class TestRotaInexistente:

    def test_retorna_404(self, client):
        assert client.get("/xyz").status_code == 404
