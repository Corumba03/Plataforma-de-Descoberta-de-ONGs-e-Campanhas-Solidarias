"""Testes unitários para as rotas da aplicação."""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from werkzeug.exceptions import NotFound
from werkzeug.security import check_password_hash

from app.main.models import AreaAtuacao, Campanha, ContatoOng, Noticia, Ong, Usuario, UserType


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
    ong.to_dict = lambda: {
        "id": str(ong.id),
        "nome": ong.nome,
        "descricao": ong.descricao,
        "cnpj": ong.cnpj,
        "area_atuacao": ong.area_atuacao.nome_area if ong.area_atuacao else None,
        "contatos": [c.to_dict() for c in ong.contatos],
        "campanhas": [c.to_dict() for c in ong.campanhas],
        "noticias": [n.to_dict() for n in ong.noticias]
    }
    return ong


def _mock_contato(**kw):
    c = MagicMock(spec=ContatoOng)
    c.tipo_contato = kw.get("tipo", "Email")
    c.valor = kw.get("valor", "contato@ong.org")
    c.id = kw.get("id", uuid.uuid4())
    c.to_dict = lambda: {"id": str(c.id), "tipo": c.tipo_contato, "valor": c.valor}
    return c


def _mock_campanha(**kw):
    c = MagicMock(spec=Campanha)
    c.titulo = kw.get("titulo", "Campanha")
    c.status = kw.get("status", "ativa")
    c.id = kw.get("id", uuid.uuid4())
    c.data_inicio = kw.get("data_inicio", date(2026, 2, 1))
    c.data_fim = kw.get("data_fim", None)
    c.descricao = kw.get("descricao", "Descrição")
    c.ong = kw.get("ong", None)
    def to_dict(include_ong=False):
        d = {
            "id": str(c.id),
            "titulo": c.titulo,
            "descricao": c.descricao,
            "status": c.status,
            "data_inicio": c.data_inicio.isoformat() if c.data_inicio else None,
            "data_fim": c.data_fim.isoformat() if c.data_fim else None,
        }
        if include_ong and c.ong:
            d["ong"] = {"id": str(c.ong.id), "nome": c.ong.nome}
        return d
    c.to_dict = to_dict
    return c


def _mock_noticia(**kw):
    n = MagicMock(spec=Noticia)
    n.titulo = kw.get("titulo", "Notícia")
    n.link = kw.get("link", None)
    n.data_publicacao = kw.get("data", datetime(2026, 4, 1))
    n.id = kw.get("id", uuid.uuid4())
    n.to_dict = lambda: {
        "id": str(n.id),
        "titulo": n.titulo,
        "data_publicacao": n.data_publicacao.isoformat() if n.data_publicacao else None,
        "link": n.link
    }
    return n


def _mock_usuario(**kw):
    u = MagicMock(spec=Usuario)
    u.id = kw.get("id", uuid.uuid4())
    u.nome = kw.get("nome", "Usuário Teste")
    u.email = kw.get("email", "usuario@teste.org")
    u.senha_hash = kw.get("senha_hash", "hash")
    u.tipo = kw.get("tipo", "usuario")
    return u

class TestIndex:

    def test_retorna_200_html(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.content_type
        assert b"Projeto iniciado com Flask" in r.data
        assert b"<a href=\"/home\">Home</a>" in r.data
        assert b"<a href=\"/health\">Health check</a>" in r.data
        assert "Nenhum usuário logado".encode() in r.data


class TestHome:

    @patch("app.main.models.Campanha.query")
    @patch("app.main.models.Ong.query")
    @patch("app.main.models.AreaAtuacao.query")
    def test_retorna_home_com_estado_vazio(self, mock_area_query, mock_ong_query, mock_camp_query, client):
        mock_area_query.all.return_value = []
        mock_ong_query.count.return_value = 0
        mock_camp_query.filter_by.return_value.count.return_value = 0

        r = client.get("/home")

        assert r.status_code == 200
        assert b"Conecte-se a <em>causas que transformam</em> comunidades" in r.data
        assert b"Nenhuma campanha ativa no momento." in r.data

    @patch("app.main.models.Campanha.query")
    @patch("app.main.models.Ong.query")
    @patch("app.main.models.AreaAtuacao.query")
    def test_retorna_home_com_campanhas_por_area(self, mock_area_query, mock_ong_query, mock_camp_query, client):
        area = MagicMock(spec=AreaAtuacao)
        area.id = uuid.uuid4()
        area.nome_area = "Educação"

        camp = _mock_campanha(titulo="Campanha Educação", status="ativa")
        camp.id = uuid.uuid4()
        camp.descricao = "Apoio escolar"
        camp.ong = _mock_ong(id=uuid.uuid4(), nome="ONG Escola")

        mock_area_query.all.return_value = [area]
        mock_ong_query.count.return_value = 5
        mock_camp_query.filter_by.return_value.count.return_value = 2
        mock_camp_query.join.return_value.filter.return_value.all.return_value = [camp]

        r = client.get("/home")

        assert r.status_code == 200
        assert "Educação".encode() in r.data
        assert b"Campanha Educa\xc3\xa7\xc3\xa3o" in r.data
        assert b"ONG Escola" in r.data
        assert b"ONGs cadastradas" in r.data
        assert b"Campanhas ativas" in r.data

    @patch("app.main.models.Campanha.query")
    @patch("app.main.models.Ong.query")
    @patch("app.main.models.AreaAtuacao.query")
    def test_home_usuario_organizador_exibe_botoes_gestao(
        self, mock_area_query, mock_ong_query, mock_camp_query, client
    ):
        mock_area_query.all.return_value = []
        mock_ong_query.count.return_value = 1
        mock_camp_query.filter_by.return_value.count.return_value = 1

        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["user_nome"] = "Ana"
            sess["tipo"] = UserType.ORGANIZADOR.value

        r = client.get("/home")

        assert r.status_code == 200
        assert "Olá, Ana".encode() in r.data
        assert b"Gerenciar Perfil" in r.data
        assert b"Gerenciar ONG" in r.data
        assert b"Login" not in r.data

    @patch("app.main.models.Campanha.query")
    @patch("app.main.models.Ong.query")
    @patch("app.main.models.AreaAtuacao.query")
    def test_home_usuario_comum_nao_exibe_botao_gerenciar_ong(
        self, mock_area_query, mock_ong_query, mock_camp_query, client
    ):
        mock_area_query.all.return_value = []
        mock_ong_query.count.return_value = 1
        mock_camp_query.filter_by.return_value.count.return_value = 1

        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["user_nome"] = "Leo"
            sess["tipo"] = "usuario"

        r = client.get("/home")

        assert r.status_code == 200
        assert "Olá, Leo".encode() in r.data
        assert b"Gerenciar Perfil" in r.data
        assert b"Gerenciar ONG" not in r.data


class TestSearchPages:

    def test_pagina_busca_ongs(self, client):
        r = client.get("/ongs")
        assert r.status_code == 200
        assert b"Buscar ONG pelo nome" in r.data

    def test_pagina_busca_campanhas(self, client):
        r = client.get("/campaigns")
        assert r.status_code == 200
        assert b"Buscar campanhas" in r.data


class TestCampaignDetail:

    @patch("app.main.models.Campanha.query")
    def test_campanha_detail_existente(self, mock_camp_query, client):
        ong = _mock_ong(id=uuid.uuid4(), nome="ONG Esperança")
        campanha = _mock_campanha(titulo="Mutirão Solidário", status="ativa")
        campanha.id = uuid.uuid4()
        campanha.descricao = "Descrição detalhada"
        campanha.data_inicio = date(2026, 3, 1)
        campanha.data_fim = date(2026, 3, 31)
        campanha.ong = ong
        mock_camp_query.get_or_404.return_value = campanha

        r = client.get(f"/campaign/{campanha.id}")

        assert r.status_code == 200
        assert b"Mutir\xc3\xa3o Solid\xc3\xa1rio" in r.data
        assert b"ONG Esperan\xc3\xa7a" in r.data
        assert b"Descri\xc3\xa7\xc3\xa3o detalhada" in r.data
        assert f"/ong/{ong.id}".encode() in r.data

    @patch("app.main.models.Campanha.query")
    def test_campanha_detail_inexistente(self, mock_camp_query, client):
        mock_camp_query.get_or_404.side_effect = NotFound()

        r = client.get(f"/campaign/{uuid.uuid4()}")

        assert r.status_code == 404

class TestHealth:

    def test_retorna_json_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.is_json
        assert r.mimetype == "application/json"
        assert r.headers["Content-Type"].startswith("application/json")

        payload = r.get_json()
        assert payload == {"status": "ok"}
        assert set(payload.keys()) == {"status"}


class TestSearchApis:

    @patch("app.main.models.Ong.query")
    def test_api_ongs_retorna_contrato(self, mock_ong_query, client):
        contato = _mock_contato(tipo="Email", valor="contato@alpha.org")
        campanha = _mock_campanha(titulo="Mutirão", status="ativa")
        campanha.data_inicio = date(2026, 1, 10)
        campanha.data_fim = None
        campanha.descricao = "Descrição campanha"
        noticia = _mock_noticia(titulo="Notícia Alpha", link="https://ex.org/noticia")
        ong = _mock_ong(
            id=uuid.uuid4(),
            nome="Alpha",
            descricao="Descrição Alpha",
            cnpj="99887766000155",
            area="Meio Ambiente",
            contatos=[contato],
            campanhas=[campanha],
            noticias=[noticia],
        )

        mock_ong_query.filter.return_value.all.return_value = [ong]

        r = client.get("/api/ongs?q=Alpha")

        assert r.status_code == 200
        assert r.is_json
        payload = r.get_json()
        assert len(payload) == 1
        assert payload[0]["nome"] == "Alpha"
        assert payload[0]["area_atuacao"] == "Meio Ambiente"
        assert payload[0]["contatos"][0]["tipo"] == "Email"
        assert payload[0]["campanhas"][0]["data_inicio"] == "2026-01-10"
        assert payload[0]["noticias"][0]["link"] == "https://ex.org/noticia"

    @patch("app.main.models.Ong.query")
    def test_api_ongs_falha_interna_retorna_contrato_de_erro(self, mock_ong_query, client):
        mock_ong_query.filter.side_effect = Exception("falha de banco")

        r = client.get("/api/ongs?q=Alpha")

        assert r.status_code == 500
        assert r.is_json
        payload = r.get_json()
        assert payload["error"]["code"] == "internal_error"
        assert payload["error"]["message"] == "erro interno ao buscar ongs"
        assert payload["error"]["details"] is None

    @patch("app.main.models.Campanha.query")
    def test_api_campanhas_retorna_lista_vazia(self, mock_camp_query, client):
        mock_camp_query.join.return_value.filter.return_value.all.return_value = []

        r = client.get("/api/campaigns?q=inexistente")

        assert r.status_code == 200
        assert r.is_json
        assert r.get_json() == []

    @patch("app.main.models.Campanha.query")
    def test_api_campanhas_retorna_contrato(self, mock_camp_query, client):
        ong = _mock_ong(id=uuid.uuid4(), nome="ONG Beta")
        campanha = _mock_campanha(titulo="Campanha Beta", status="ativa")
        campanha.id = uuid.uuid4()
        campanha.descricao = "Desc"
        campanha.data_inicio = date(2026, 2, 1)
        campanha.data_fim = date(2026, 2, 28)
        campanha.ong = ong

        mock_camp_query.join.return_value.filter.return_value.all.return_value = [campanha]

        r = client.get("/api/campaigns?q=Beta")

        assert r.status_code == 200
        assert r.is_json
        payload = r.get_json()
        assert len(payload) == 1
        assert payload[0]["titulo"] == "Campanha Beta"
        assert payload[0]["status"] == "ativa"
        assert payload[0]["data_inicio"] == "2026-02-01"
        assert payload[0]["ong"]["nome"] == "ONG Beta"

    @patch("app.main.models.Campanha.query")
    def test_api_campanhas_falha_interna_retorna_contrato_de_erro(self, mock_camp_query, client):
        mock_camp_query.join.side_effect = Exception("falha de banco")

        r = client.get("/api/campaigns?q=Beta")

        assert r.status_code == 500
        assert r.is_json
        payload = r.get_json()
        assert payload["error"]["code"] == "internal_error"
        assert payload["error"]["message"] == "erro interno ao buscar campanhas"
        assert payload["error"]["details"] is None

class TestOngProfile:

    @patch("app.main.models.db.get_or_404")
    def test_ong_existente(self, mock_get, client):
        ong = _mock_ong(nome="Alpha", cnpj="99887766000155", area="Meio Ambiente")
        mock_get.return_value = ong

        r = client.get(f"/ong/{ong.id}")

        assert r.status_code == 200
        mock_get.assert_called_once_with(Ong, ong.id)
        assert b"Alpha" in r.data
        assert b"99887766000155" in r.data
        assert "Meio Ambiente".encode() in r.data

    @patch("app.main.models.db.get_or_404")
    def test_ong_inexistente(self, mock_get, client):
        mock_get.side_effect = NotFound()
        r = client.get(f"/ong/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_id_invalido(self, client):
        r = client.get("/ong/nao-e-uuid")
        assert r.status_code == 404

    @patch("app.main.models.db.get_or_404")
    def test_exibe_contatos(self, mock_get, client):
        ong = _mock_ong(contatos=[_mock_contato(valor="x@y.org")])
        mock_get.return_value = ong

        r = client.get(f"/ong/{ong.id}")
        assert b"x@y.org" in r.data

    @patch("app.main.models.db.get_or_404")
    def test_sem_contatos(self, mock_get, client):
        mock_get.return_value = _mock_ong(contatos=[])
        ong_id = mock_get.return_value.id

        r = client.get(f"/ong/{ong_id}")
        assert "Nenhum contato cadastrado".encode() in r.data

    @patch("app.main.models.db.get_or_404")
    def test_exibe_campanhas(self, mock_get, client):
        ong = _mock_ong(campanhas=[_mock_campanha(titulo="Camp Visível")])
        mock_get.return_value = ong

        r = client.get(f"/ong/{ong.id}")
        assert "Camp Visível".encode() in r.data

    @patch("app.main.models.db.get_or_404")
    def test_sem_campanhas(self, mock_get, client):
        mock_get.return_value = _mock_ong(campanhas=[])
        r = client.get(f"/ong/{mock_get.return_value.id}")
        assert "Nenhuma campanha no momento".encode() in r.data

    @patch("app.main.models.db.get_or_404")
    def test_exibe_noticias_com_link(self, mock_get, client):
        n = _mock_noticia(titulo="Nova", link="https://ex.org/n")
        mock_get.return_value = _mock_ong(noticias=[n])

        r = client.get(f"/ong/{mock_get.return_value.id}")
        assert b"Nova" in r.data
        assert b"https://ex.org/n" in r.data
        assert b"<a " in r.data

    @patch("app.main.models.db.get_or_404")
    def test_sem_noticias(self, mock_get, client):
        mock_get.return_value = _mock_ong(noticias=[])
        r = client.get(f"/ong/{mock_get.return_value.id}")
        assert "Nenhuma notícia recente".encode() in r.data


class TestAuth:

    def test_login_get(self, client):
        r = client.get("/auth/login")
        assert r.status_code == 200
        assert b"Entrar" in r.data

    def test_register_get(self, client):
        r = client.get("/auth/register")
        assert r.status_code == 200
        assert b"Criar conta" in r.data

    @patch("app.main.models.Usuario.query")
    def test_register_post_usuario_existente(self, mock_user_query, client):
        mock_user_query.filter_by.return_value.first.return_value = _mock_usuario()

        r = client.post(
            "/auth/register",
            data={"nome": "Teste", "email": "usuario@teste.org", "senha": "123", "tipo": "usuario"},
        )

        assert r.status_code == 400
        assert "text/html" in r.content_type
        assert "Usuário já existe".encode() in r.data

    @patch("app.main.models.db.session.commit")
    @patch("app.main.models.db.session.add")
    @patch("app.main.models.Usuario.query")
    def test_register_post_sucesso_cria_sessao_e_redireciona(
        self, mock_user_query, mock_add, mock_commit, client
    ):
        mock_user_query.filter_by.return_value.first.return_value = None

        r = client.post(
            "/auth/register",
            data={
                "nome": "Nova Pessoa",
                "email": "nova@teste.org",
                "senha": "segredo",
                "tipo": UserType.ORGANIZADOR.value,
            },
        )

        assert r.status_code == 302
        assert r.headers["Location"].endswith("/home")
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        with client.session_transaction() as sess:
            assert "user_id" in sess
            assert sess["tipo"] == UserType.ORGANIZADOR.value

    def test_register_post_sucesso_persiste_usuario_real(self, client, db):
        email = "persistencia@teste.org"

        r = client.post(
            "/auth/register",
            data={
                "nome": "Pessoa Real",
                "email": email,
                "senha": "segredo-real",
                "tipo": "usuario",
            },
        )

        assert r.status_code == 302
        assert r.headers["Location"].endswith("/home")

        user = db.session.query(Usuario).filter_by(email=email).first()
        assert user is not None
        assert user.nome == "Pessoa Real"
        assert user.senha_hash != "segredo-real"
        assert check_password_hash(user.senha_hash, "segredo-real")

        with client.session_transaction() as sess:
            assert sess["user_id"] == str(user.id)
            assert sess["tipo"] == "usuario"

    @patch("app.main.controllers.auth_controller.check_password_hash")
    @patch("app.main.models.Usuario.query")
    def test_login_post_sucesso_seta_sessao(self, mock_user_query, mock_check_hash, client):
        user = _mock_usuario(id=uuid.uuid4(), nome="Maria", tipo=UserType.ORGANIZADOR.value)
        mock_user_query.filter_by.return_value.first.return_value = user
        mock_check_hash.return_value = True

        r = client.post("/auth/login", data={"email": user.email, "senha": "segredo"})

        assert r.status_code == 302
        assert r.headers["Location"].endswith("/home")
        with client.session_transaction() as sess:
            assert sess["user_id"] == str(user.id)
            assert sess["user_nome"] == "Maria"
            assert sess["tipo"] == UserType.ORGANIZADOR.value

    @patch("app.main.models.Usuario.query")
    def test_login_post_credenciais_invalidas(self, mock_user_query, client):
        mock_user_query.filter_by.return_value.first.return_value = None

        r = client.post("/auth/login", data={"email": "x@x.com", "senha": "errada"})

        assert r.status_code == 200
        assert "text/html" in r.content_type
        assert b"Entrar" in r.data

    @patch("app.main.controllers.auth_controller.check_password_hash")
    @patch("app.main.models.Usuario.query")
    def test_login_post_usuario_existente_senha_invalida(self, mock_user_query, mock_check_hash, client):
        mock_user_query.filter_by.return_value.first.return_value = _mock_usuario()
        mock_check_hash.return_value = False

        r = client.post("/auth/login", data={"email": "usuario@teste.org", "senha": "invalida"})

        assert r.status_code == 200
        assert "text/html" in r.content_type
        assert b"Entrar" in r.data

    def test_logout_redireciona_para_index_quando_page_index(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())

        r = client.post("/auth/logout?page=index")

        assert r.status_code == 302
        assert r.headers["Location"].endswith("/")
        with client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_logout_redireciona_para_home_por_padrao(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())

        r = client.post("/auth/logout")

        assert r.status_code == 302
        assert r.headers["Location"].endswith("/home")


class TestEditPages:

    def test_edit_user_sem_login_redireciona(self, client):
        r = client.get("/edit/user")
        assert r.status_code == 302
        assert "/auth/login" in r.headers["Location"]

    @patch("app.main.models.db.get_or_404")
    def test_edit_user_logado_renderiza_pagina(self, mock_get, client):
        user = _mock_usuario(id=uuid.uuid4(), nome="João", email="joao@ex.org", tipo="usuario")
        mock_get.return_value = user

        with client.session_transaction() as sess:
            sess["user_id"] = str(user.id)

        r = client.get("/edit/user")

        assert r.status_code == 200
        assert "Editar Usuário".encode() in r.data
        assert b"joao@ex.org" in r.data

    def test_edit_ong_sem_login_redireciona(self, client):
        r = client.get(f"/edit/ong/{uuid.uuid4()}")
        assert r.status_code == 302
        assert "/auth/login" in r.headers["Location"]

    @patch("app.main.models.db.get_or_404")
    def test_edit_ong_usuario_sem_permissao(self, mock_get, client):
        mock_get.return_value = _mock_ong(id=uuid.uuid4())
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["tipo"] = "usuario"

        r = client.get(f"/edit/ong/{uuid.uuid4()}")

        assert r.status_code == 403
        assert b"Acesso negado" in r.data

    @patch("app.main.models.db.get_or_404")
    def test_edit_ong_organizador_renderiza_pagina(self, mock_get, client):
        ong = _mock_ong(id=uuid.uuid4(), nome="ONG Edit")
        mock_get.return_value = ong
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["tipo"] = UserType.ORGANIZADOR.value

        r = client.get(f"/edit/ong/{ong.id}")

        assert r.status_code == 200
        assert b"Editar ONG" in r.data
        assert b"ONG Edit" in r.data


class TestUpdateApis:

    @patch("app.main.models.db.get_or_404")
    @patch("app.main.models.db.session.commit")
    def test_update_ong_retorna_sucesso(self, mock_commit, mock_get, client):
        ong = _mock_ong(id=uuid.uuid4(), nome="Orig", descricao="D", cnpj="12345678000199")
        mock_get.return_value = ong

        r = client.put(
            f"/api/ongs/{ong.id}",
            json={"nome": "Novo Nome", "descricao": "Nova Descrição", "cnpj": "99887766000155"},
        )

        assert r.status_code == 200
        assert r.is_json
        assert r.mimetype == "application/json"
        assert r.get_json()["message"] == "ONG atualizada com sucesso"
        assert ong.nome == "Novo Nome"
        assert ong.descricao == "Nova Descrição"
        assert ong.cnpj == "99887766000155"
        mock_commit.assert_called_once()

    @patch("app.main.models.db.get_or_404")
    @patch("app.main.models.db.session.commit")
    def test_update_ong_retorna_404_quando_nao_encontra(self, mock_commit, mock_get, client):
        mock_get.side_effect = NotFound()

        r = client.put(
            f"/api/ongs/{uuid.uuid4()}",
            json={"nome": "Novo Nome"},
        )

        assert r.status_code == 404
        assert r.is_json
        payload = r.get_json()
        assert payload["error"]["code"] == "not_found"
        assert payload["error"]["message"] == "recurso não encontrado"
        assert payload["error"]["details"] is None
        mock_commit.assert_not_called()

    @patch("app.main.models.db.session.commit")
    def test_update_ong_payload_invalido_retorna_400(self, mock_commit, client):
        r = client.put(
            f"/api/ongs/{uuid.uuid4()}",
            data="nao-json",
            headers={"Content-Type": "text/plain"},
        )

        assert r.status_code == 400
        assert r.is_json
        payload = r.get_json()
        assert payload["error"]["code"] == "invalid_payload"
        assert payload["error"]["message"] == "payload JSON inválido"
        assert payload["error"]["details"] is None
        mock_commit.assert_not_called()

    @patch("app.main.models.db.get_or_404")
    @patch("app.main.models.db.session.commit")
    def test_update_user_atualiza_sessao(self, mock_commit, mock_get, client):
        user = _mock_usuario(id=uuid.uuid4(), nome="Ana", email="ana@old.org", tipo="usuario")
        mock_get.return_value = user

        with client.session_transaction() as sess:
            sess["user_nome"] = "Nome Antigo"

        r = client.put(
            f"/api/users/{user.id}",
            json={"nome": "Ana Nova", "email": "ana@new.org"},
        )

        assert r.status_code == 200
        assert r.is_json
        assert r.mimetype == "application/json"
        assert r.get_json()["message"] == "Usuário atualizado com sucesso"
        assert user.nome == "Ana Nova"
        assert user.email == "ana@new.org"
        with client.session_transaction() as sess:
            assert sess["user_nome"] == "Ana Nova"
        mock_commit.assert_called_once()

    @patch("app.main.controllers.user_controller.generate_password_hash")
    @patch("app.main.models.db.get_or_404")
    @patch("app.main.models.db.session.commit")
    def test_update_user_com_senha_rehash(self, mock_commit, mock_get, mock_hash, client):
        user = _mock_usuario(id=uuid.uuid4(), nome="Lia", email="lia@old.org", senha_hash="hash-antigo")
        mock_get.return_value = user
        mock_hash.return_value = "hash-novo"

        r = client.put(
            f"/api/users/{user.id}",
            json={"senha": "nova-senha"},
        )

        assert r.status_code == 200
        assert r.is_json
        assert user.senha_hash == "hash-novo"
        mock_hash.assert_called_once_with("nova-senha")
        mock_commit.assert_called_once()

    @patch("app.main.models.db.get_or_404")
    @patch("app.main.models.db.session.commit")
    def test_update_user_retorna_404_quando_nao_encontra(self, mock_commit, mock_get, client):
        mock_get.side_effect = NotFound()

        r = client.put(
            f"/api/users/{uuid.uuid4()}",
            json={"nome": "Qualquer"},
        )

        assert r.status_code == 404
        assert r.is_json
        payload = r.get_json()
        assert payload["error"]["code"] == "not_found"
        assert payload["error"]["message"] == "recurso não encontrado"
        assert payload["error"]["details"] is None
        mock_commit.assert_not_called()

    @patch("app.main.models.db.session.commit")
    def test_update_user_payload_invalido_retorna_400(self, mock_commit, client):
        r = client.put(
            f"/api/users/{uuid.uuid4()}",
            data="nao-json",
            headers={"Content-Type": "text/plain"},
        )

        assert r.status_code == 400
        assert r.is_json
        payload = r.get_json()
        assert payload["error"]["code"] == "invalid_payload"
        assert payload["error"]["message"] == "payload JSON inválido"
        assert payload["error"]["details"] is None
        mock_commit.assert_not_called()

class TestRotaInexistente:

    def test_retorna_404(self, client):
        assert client.get("/xyz").status_code == 404


class TestInteresseRoutes:

    @patch("app.main.repositories.InteresseVoluntariadoRepository")
    def test_demonstrar_interesse_deslogado(self, mock_repo, client):
        r = client.post(f"/ong/{uuid.uuid4()}/interesse", data={"mensagem": "Quero ajudar"}, follow_redirects=True)
        assert "/auth/login" in r.request.path
        assert "Você precisa estar logado" in r.get_data(as_text=True)

    @patch("app.main.repositories.InteresseVoluntariadoRepository")
    def test_demonstrar_interesse_como_organizador(self, mock_repo, client):
        user_id = uuid.uuid4()
        with client.session_transaction() as sess:
            sess["user_id"] = str(user_id)
            sess["tipo"] = UserType.ORGANIZADOR.value

        ong_id = uuid.uuid4()
        with patch("app.main.models.db.get_or_404") as mock_get:
            ong = MagicMock(spec=Ong)
            ong.dono = MagicMock(id=user_id)
            mock_get.return_value = ong
            r = client.post(f"/ong/{ong_id}/interesse", data={"mensagem": "Quero ajudar"}, follow_redirects=True)
            assert f"/ong/{ong_id}" in r.request.path
            assert "Organizadores não podem se voluntariar" in r.get_data(as_text=True)

    @patch("app.main.repositories.InteresseVoluntariadoRepository")
    def test_demonstrar_interesse_mensagem_vazia(self, mock_repo, client):
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["tipo"] = UserType.VOLUNTARIO.value

        ong_id = uuid.uuid4()
        with patch("app.main.models.db.get_or_404") as mock_get:
            mock_get.return_value = MagicMock(spec=Ong)
            r = client.post(f"/ong/{ong_id}/interesse", data={"mensagem": ""}, follow_redirects=True)
            assert f"/ong/{ong_id}" in r.request.path
            assert "A mensagem de interesse não pode estar vazia" in r.get_data(as_text=True)

    @patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
    def test_demonstrar_interesse_sucesso(self, mock_repo, client):
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["tipo"] = UserType.VOLUNTARIO.value

        mock_instance = mock_repo.return_value
        ong_id = uuid.uuid4()
        with patch("app.main.models.db.get_or_404") as mock_get:
            mock_get.return_value = MagicMock(spec=Ong)
            r = client.post(f"/ong/{ong_id}/interesse", data={"mensagem": "Quero ajudar"}, follow_redirects=True)
            assert f"/ong/{ong_id}" in r.request.path
            assert "Interesse demonstrado com sucesso" in r.get_data(as_text=True)
            mock_instance.add.assert_called_once()

    def test_meus_interesses_deslogado(self, client):
        r = client.get("/meus-interesses")
        assert r.status_code == 302
        assert "/auth/login" in r.location

    @patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
    def test_meus_interesses_sucesso(self, mock_repo, client):
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["tipo"] = UserType.VOLUNTARIO.value

        mock_instance = mock_repo.return_value
        mock_instance.get_by_usuario.return_value = []

        r = client.get("/meus-interesses")
        assert r.status_code == 200

    def test_interesses_recebidos_deslogado(self, client):
        r = client.get(f"/ong/{uuid.uuid4()}/interesses")
        assert r.status_code == 302

    def test_interesses_recebidos_como_voluntario(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["tipo"] = UserType.VOLUNTARIO.value

        r = client.get(f"/ong/{uuid.uuid4()}/interesses")
        assert r.status_code == 403

    @patch("app.main.models.db.get_or_404")
    @patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
    def test_interesses_recebidos_como_organizador(self, mock_repo, mock_get, client):
        with client.session_transaction() as sess:
            sess["user_id"] = str(uuid.uuid4())
            sess["tipo"] = UserType.ORGANIZADOR.value

        ong = MagicMock(spec=Ong)
        ong.id = uuid.uuid4()
        ong.nome = "ONG Teste"
        mock_get.return_value = ong

        mock_instance = mock_repo.return_value
        mock_instance.get_by_ong.return_value = []

        r = client.get(f"/ong/{ong.id}/interesses")
        assert r.status_code == 200
        mock_instance.get_by_ong.assert_called_once_with(ong.id)



