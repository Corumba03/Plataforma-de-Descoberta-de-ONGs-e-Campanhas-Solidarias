import uuid
from unittest.mock import patch

from werkzeug.exceptions import NotFound

from app.main.models import AreaAtuacao, Ong, Usuario, UserType

'''Tests para o controller de usuarios.
1) Testa a edição e atualização de usuário, incluindo payload inválido, rehash de senha e recurso inexistente.
2) Testa a rota /my-ongs com autenticação, autorização e filtro por dono.
3) Testa a rota /api/allusers retornando o contrato esperado.'''


def _create_area(db, nome_area="Educacao"):
    area = AreaAtuacao(nome_area=nome_area)
    db.session.add(area)
    db.session.flush()
    return area


def _create_user(db, nome="Usuario", email="user@teste.com", tipo=UserType.VOLUNTARIO.value):
    user = Usuario(nome=nome, email=email, senha_hash="hash", tipo=tipo)
    db.session.add(user)
    db.session.flush()
    return user


def _create_ong(db, area, dono, nome="ONG Teste", cnpj="12345678000199"):
    ong = Ong(
        nome=nome,
        descricao="Descricao da ONG",
        cnpj=cnpj,
        id_area_atuacao=area.id,
        id_dono=dono.id,
    )
    db.session.add(ong)
    db.session.flush()
    return ong


def _login_as(client, user_id, tipo):
    with client.session_transaction() as sess:
        sess["user_id"] = str(user_id)
        sess["tipo"] = tipo


def test_edit_user_sem_login_redireciona(client):
    response = client.get("/edit/user")

    assert response.status_code == 302
    assert "/auth/login" in response.location


@patch("app.main.models.db.get_or_404")
def test_edit_user_logado_renderiza_pagina(mock_get, client):
    user = Usuario(id=uuid.uuid4(), nome="Joao", email="joao@ex.org", senha_hash="hash", tipo="usuario")
    mock_get.return_value = user
    _login_as(client, user.id, UserType.VOLUNTARIO.value)

    response = client.get("/edit/user")

    assert response.status_code == 200
    assert b"Editar Usu" in response.data
    assert b"joao@ex.org" in response.data


@patch("app.main.models.db.get_or_404")
@patch("app.main.models.db.session.commit")
def test_update_user_atualiza_sessao(mock_commit, mock_get, client):
    user = Usuario(id=uuid.uuid4(), nome="Ana", email="ana@old.org", senha_hash="hash", tipo="usuario")
    mock_get.return_value = user

    with client.session_transaction() as sess:
        sess["user_nome"] = "Nome Antigo"

    response = client.put(
        f"/api/users/{user.id}",
        json={"nome": "Ana Nova", "email": "ana@new.org"},
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()["message"] == "Usuário atualizado com sucesso"
    assert user.nome == "Ana Nova"
    assert user.email == "ana@new.org"
    with client.session_transaction() as sess:
        assert sess["user_nome"] == "Ana Nova"
    mock_commit.assert_called_once()


@patch("app.main.controllers.user_controller.generate_password_hash")
@patch("app.main.models.db.get_or_404")
@patch("app.main.models.db.session.commit")
def test_update_user_com_senha_rehash(mock_commit, mock_get, mock_hash, client):
    user = Usuario(id=uuid.uuid4(), nome="Lia", email="lia@old.org", senha_hash="hash-antigo", tipo="usuario")
    mock_get.return_value = user
    mock_hash.return_value = "hash-novo"

    response = client.put(
        f"/api/users/{user.id}",
        json={"senha": "nova-senha"},
    )

    assert response.status_code == 200
    assert response.is_json
    assert user.senha_hash == "hash-novo"
    mock_hash.assert_called_once_with("nova-senha")
    mock_commit.assert_called_once()


@patch("app.main.models.db.get_or_404")
@patch("app.main.models.db.session.commit")
def test_update_user_retorna_404_quando_nao_encontra(mock_commit, mock_get, client):
    mock_get.side_effect = NotFound()

    response = client.put(
        f"/api/users/{uuid.uuid4()}",
        json={"nome": "Qualquer"},
    )

    assert response.status_code == 404
    assert response.is_json
    payload = response.get_json()
    assert payload["error"]["code"] == "not_found"
    assert payload["error"]["message"] == "recurso não encontrado"
    assert payload["error"]["details"] is None
    mock_commit.assert_not_called()


@patch("app.main.models.db.session.commit")
def test_update_user_payload_invalido_retorna_400(mock_commit, client):
    response = client.put(
        f"/api/users/{uuid.uuid4()}",
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


def test_my_ongs_sem_login_redireciona(client):
    response = client.get("/my-ongs")

    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_my_ongs_sem_permissao_retorna_403(client):
    _login_as(client, uuid.uuid4(), UserType.VOLUNTARIO.value)

    response = client.get("/my-ongs")

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Acesso negado"


def test_my_ongs_filtra_por_dono(client, db):
    area = _create_area(db)
    dono = _create_user(db, nome="Dono", email="dono@teste.com", tipo=UserType.ORGANIZADOR.value)
    outro = _create_user(db, nome="Outro", email="outro@teste.com", tipo=UserType.ORGANIZADOR.value)
    _create_ong(db, area, dono, nome="ONG Minha", cnpj="77777777000177")
    _create_ong(db, area, outro, nome="ONG Alheia", cnpj="88888888000188")
    db.session.commit()
    _login_as(client, dono.id, UserType.ORGANIZADOR.value)

    response = client.get("/my-ongs")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "ONG Minha" in page
    assert "ONG Alheia" not in page


def test_get_all_users_retorna_lista(client, db):
    user1 = _create_user(db, nome="Ana", email="ana@teste.com")
    user2 = _create_user(db, nome="Beto", email="beto@teste.com", tipo=UserType.ORGANIZADOR.value)
    db.session.commit()

    response = client.get("/api/allusers")

    assert response.status_code == 200
    assert response.is_json
    payload = response.get_json()
    assert len(payload) == 2
    assert payload[0]["id"] == str(user1.id)
    assert payload[0]["nome"] == "Ana"
    assert payload[0]["email"] == "ana@teste.com"
    assert payload[1]["id"] == str(user2.id)
    assert payload[1]["nome"] == "Beto"
    assert payload[1]["email"] == "beto@teste.com"