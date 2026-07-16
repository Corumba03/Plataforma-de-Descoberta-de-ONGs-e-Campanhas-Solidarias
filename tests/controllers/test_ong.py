import uuid
from unittest.mock import MagicMock, patch

from werkzeug.exceptions import NotFound

from app.main.models import AreaAtuacao, Ong, Usuario, UserType

'''Tests para o controller de ongs.
1) Testa busca e API de ongs, incluindo sucesso e falha interna.
2) Testa a edição e atualização de ONG, incluindo payload inválido e recurso inexistente.
3) Testa a criação e deleção de ONG, incluindo autenticação, autorização e permissão por dono.'''


def _create_area(db, nome_area="Educacao"):
    area = AreaAtuacao(nome_area=nome_area)
    db.session.add(area)
    db.session.flush()
    return area


def _create_user(db, nome="Organizador", email="org@teste.com", tipo=UserType.ORGANIZADOR.value):
    user = Usuario(nome=nome, email=email, senha_hash="hash", tipo=tipo)
    db.session.add(user)
    db.session.flush()
    return user


def _create_ong(db, area, dono=None, nome="ONG Teste", cnpj="12345678000199"):
    ong = Ong(
        nome=nome,
        descricao="Descricao da ONG",
        cnpj=cnpj,
        id_area_atuacao=area.id,
        id_dono=dono.id if dono else None,
    )
    db.session.add(ong)
    db.session.flush()
    return ong


def _login_as(client, user_id, tipo):
    with client.session_transaction() as sess:
        sess["user_id"] = str(user_id)
        sess["tipo"] = tipo


def test_pagina_busca_ongs(client):
    response = client.get("/ongs")

    assert response.status_code == 200
    assert b"Buscar ONG pelo nome" in response.data


def test_api_ongs_retorna_dados(client, db):
    area = _create_area(db, nome_area="Saude")
    _create_ong(db, area, nome="ONG Alpha", cnpj="11111111000111")
    db.session.commit()

    response = client.get("/api/ongs?q=Alpha")

    assert response.status_code == 200
    assert response.is_json
    payload = response.get_json()
    assert len(payload) == 1
    assert payload[0]["nome"] == "ONG Alpha"
    assert payload[0]["area_atuacao"] == "Saude"


@patch("app.main.models.Ong.query")
def test_api_ongs_falha_interna_retorna_500(mock_ong_query, client):
    mock_ong_query.filter.side_effect = Exception("falha de banco")

    response = client.get("/api/ongs?q=Alpha")

    assert response.status_code == 500
    assert response.is_json
    payload = response.get_json()
    assert payload["error"]["code"] == "internal_error"
    assert payload["error"]["message"] == "erro interno ao buscar ongs"
    assert payload["error"]["details"] is None


@patch("app.main.models.db.get_or_404")
@patch("app.main.models.db.session.commit")
def test_update_ong_retorna_sucesso(mock_commit, mock_get, client):
    ong = MagicMock(spec=Ong)
    ong.id = uuid.uuid4()
    ong.nome = "Orig"
    ong.descricao = "D"
    ong.cnpj = "12345678000199"
    mock_get.return_value = ong

    response = client.put(
        f"/api/ongs/{ong.id}",
        json={"nome": "Novo Nome", "descricao": "Nova Descricao", "cnpj": "99887766000155"},
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()["message"] == "ONG atualizada com sucesso"
    assert ong.nome == "Novo Nome"
    assert ong.descricao == "Nova Descricao"
    assert ong.cnpj == "99887766000155"
    mock_commit.assert_called_once()


@patch("app.main.models.db.get_or_404")
@patch("app.main.models.db.session.commit")
def test_update_ong_retorna_404_quando_nao_encontra(mock_commit, mock_get, client):
    mock_get.side_effect = NotFound()

    response = client.put(
        f"/api/ongs/{uuid.uuid4()}",
        json={"nome": "Novo Nome"},
    )

    assert response.status_code == 404
    assert response.is_json
    payload = response.get_json()
    assert payload["error"]["code"] == "not_found"
    assert payload["error"]["message"] == "recurso não encontrado"
    assert payload["error"]["details"] is None
    mock_commit.assert_not_called()


@patch("app.main.models.db.session.commit")
def test_update_ong_payload_invalido_retorna_400(mock_commit, client):
    response = client.put(
        f"/api/ongs/{uuid.uuid4()}",
        data="nao-json",
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 400
    assert response.is_json
    payload = response.get_json()
    assert payload["error"]["code"] == "invalid_payload"
    assert payload["error"]["message"] == "payload JSON inválido"
    assert payload["error"]["details"] is None
    mock_commit.assert_not_called()


def test_edit_ong_sem_login_redireciona(client):
    response = client.get(f"/edit/ong/{uuid.uuid4()}")

    assert response.status_code == 302
    assert "/auth/login" in response.location


@patch("app.main.models.db.get_or_404")
def test_edit_ong_usuario_sem_permissao(mock_get, client):
    mock_get.return_value = MagicMock(spec=Ong)
    _login_as(client, uuid.uuid4(), UserType.VOLUNTARIO.value)

    response = client.get(f"/edit/ong/{uuid.uuid4()}")

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Acesso negado"


@patch("app.main.controllers.ong_controller.AreaAtuacao.query")
@patch("app.main.models.db.get_or_404")
def test_edit_ong_organizador_renderiza_pagina(mock_get, mock_area_query, client):
    ong = MagicMock(spec=Ong)
    ong.id = uuid.uuid4()
    ong.nome = "ONG Edit"
    ong.contatos = []
    ong.campanhas = []
    ong.noticias = []
    mock_get.return_value = ong
    mock_area_query.all.return_value = []
    _login_as(client, uuid.uuid4(), UserType.ORGANIZADOR.value)

    response = client.get(f"/edit/ong/{ong.id}")

    assert response.status_code == 200
    assert b"Editar ONG" in response.data
    assert b"ONG Edit" in response.data


def test_create_ong_sem_login_redireciona(client):
    response = client.post("/api/ong", json={})

    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_create_ong_sem_permissao_retorna_403(client):
    _login_as(client, uuid.uuid4(), UserType.VOLUNTARIO.value)

    response = client.post("/api/ong", json={})

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Acesso negado"


def test_create_ong_payload_invalido_retorna_400(client):
    _login_as(client, uuid.uuid4(), UserType.ORGANIZADOR.value)

    response = client.post(
        "/api/ong",
        data="nao-json",
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 400
    assert response.is_json
    payload = response.get_json()
    assert payload["error"]["code"] == "invalid_payload"
    assert payload["error"]["message"] == "payload JSON inválido"


def test_create_ong_sucesso(client, db):
    area = _create_area(db, nome_area="Meio Ambiente")
    user = _create_user(db, email="criador@teste.com")
    db.session.commit()
    _login_as(client, user.id, UserType.ORGANIZADOR.value)

    response = client.post(
        "/api/ong",
        json={
            "nome": "ONG Nova",
            "descricao": "Descricao nova",
            "cnpj": "44444444000144",
            "id_area_atuacao": str(area.id),
        },
    )

    assert response.status_code == 201
    assert response.is_json
    payload = response.get_json()
    assert payload["message"] == "ONG criada com sucesso"

    ong = db.session.query(Ong).filter_by(id=uuid.UUID(payload["id"])).first()
    assert ong is not None
    assert ong.nome == "ONG Nova"
    assert ong.id_dono == user.id


def test_delete_ong_sem_login_redireciona(client):
    response = client.delete(f"/api/ong/{uuid.uuid4()}")

    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_delete_ong_sem_permissao_retorna_403(client):
    _login_as(client, uuid.uuid4(), UserType.VOLUNTARIO.value)

    response = client.delete(f"/api/ong/{uuid.uuid4()}")

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Acesso negado"


def test_delete_ong_inexistente_retorna_404(client, db):
    _login_as(client, uuid.uuid4(), UserType.ORGANIZADOR.value)

    response = client.delete(f"/api/ong/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.is_json
    payload = response.get_json()
    assert payload["error"]["code"] == "not_found"
    assert payload["error"]["message"] == "ONG não encontrada"


def test_delete_ong_sem_ser_dono_retorna_403(client, db):
    area = _create_area(db)
    dono = _create_user(db, email="dono@teste.com")
    outro = _create_user(db, email="outro@teste.com")
    ong = _create_ong(db, area, dono=dono, nome="ONG Dono", cnpj="55555555000155")
    db.session.commit()
    _login_as(client, outro.id, UserType.ORGANIZADOR.value)

    response = client.delete(f"/api/ong/{ong.id}")

    assert response.status_code == 403
    assert response.is_json
    payload = response.get_json()
    assert payload["error"]["code"] == "forbidden"
    assert payload["error"]["message"] == "sem permissão para deletar esta ONG"


def test_delete_ong_sucesso(client, db):
    area = _create_area(db)
    dono = _create_user(db, email="remover@teste.com")
    ong = _create_ong(db, area, dono=dono, nome="ONG Remover", cnpj="66666666000166")
    db.session.commit()
    _login_as(client, dono.id, UserType.ORGANIZADOR.value)

    response = client.delete(f"/api/ong/{ong.id}")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()["message"] == "ONG deletada com sucesso"
    assert db.session.query(Ong).filter_by(id=ong.id).first() is None