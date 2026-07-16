import uuid
from unittest.mock import MagicMock, patch

from app.main.models import Ong, UserType

'''Tests para o controller de interesses.
1) Testa a rota POST /ong/<uuid:ong_id>/interesse para usuário deslogado, organizador, mensagem vazia e sucesso.
2) Testa a rota GET /meus-interesses para usuário deslogado e autenticado.
3) Testa a rota GET /ong/<uuid:ong_id>/interesses para usuário deslogado, voluntário e organizador.'''


def _login_as(client, tipo):
    with client.session_transaction() as sess:
        sess["user_id"] = str(uuid.uuid4())
        sess["tipo"] = tipo


@patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
def test_demonstrar_interesse_deslogado(mock_repo, client):
    ong_id = uuid.uuid4()

    response = client.post(
        f"/ong/{ong_id}/interesse",
        data={"mensagem": "Quero ajudar"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "/auth/login" in response.request.path
    assert "Você precisa estar logado" in response.get_data(as_text=True)
    mock_repo.assert_not_called()


@patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
def test_demonstrar_interesse_como_organizador(mock_repo, client):
    _login_as(client, UserType.ORGANIZADOR.value)
    ong_id = uuid.uuid4()

    response = client.post(
        f"/ong/{ong_id}/interesse",
        data={"mensagem": "Quero ajudar"},
    )

    assert response.status_code == 302
    assert response.location.endswith(f"/ong/{ong_id}")
    with client.session_transaction() as sess:
        assert ("danger", "Organizadores não podem se voluntariar.") in sess.get("_flashes", [])
    mock_repo.assert_not_called()


@patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
def test_demonstrar_interesse_mensagem_vazia(mock_repo, client):
    _login_as(client, UserType.VOLUNTARIO.value)
    ong_id = uuid.uuid4()

    response = client.post(
        f"/ong/{ong_id}/interesse",
        data={"mensagem": "   "},
    )

    assert response.status_code == 302
    assert response.location.endswith(f"/ong/{ong_id}")
    with client.session_transaction() as sess:
        assert ("danger", "A mensagem de interesse não pode estar vazia.") in sess.get("_flashes", [])
    mock_repo.assert_not_called()


@patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
def test_demonstrar_interesse_sucesso(mock_repo, client):
    user_id = uuid.uuid4()
    with client.session_transaction() as sess:
        sess["user_id"] = str(user_id)
        sess["tipo"] = UserType.VOLUNTARIO.value

    mock_instance = mock_repo.return_value
    ong_id = uuid.uuid4()

    response = client.post(
        f"/ong/{ong_id}/interesse",
        data={"mensagem": "Quero ajudar"},
    )

    assert response.status_code == 302
    assert response.location.endswith(f"/ong/{ong_id}")
    with client.session_transaction() as sess:
        assert ("success", "Interesse demonstrado com sucesso!") in sess.get("_flashes", [])
    mock_instance.add.assert_called_once_with(id_usuario=user_id, id_ong=ong_id, mensagem="Quero ajudar")


def test_meus_interesses_deslogado(client):
    response = client.get("/meus-interesses")

    assert response.status_code == 302
    assert "/auth/login" in response.location


@patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
def test_meus_interesses_sucesso(mock_repo, client):
    user_id = uuid.uuid4()
    with client.session_transaction() as sess:
        sess["user_id"] = str(user_id)
        sess["tipo"] = UserType.VOLUNTARIO.value

    mock_instance = mock_repo.return_value
    mock_instance.get_by_usuario.return_value = []

    response = client.get("/meus-interesses")

    assert response.status_code == 200
    mock_instance.get_by_usuario.assert_called_once_with(user_id)


def test_interesses_recebidos_deslogado(client):
    response = client.get(f"/ong/{uuid.uuid4()}/interesses")

    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_interesses_recebidos_como_voluntario(client):
    _login_as(client, UserType.VOLUNTARIO.value)

    response = client.get(f"/ong/{uuid.uuid4()}/interesses")

    assert response.status_code == 403
    assert response.get_data(as_text=True) == "Acesso negado"


@patch("app.main.models.db.get_or_404")
@patch("app.main.controllers.interesse_controller.InteresseVoluntariadoRepository")
def test_interesses_recebidos_como_organizador(mock_repo, mock_get, client):
    _login_as(client, UserType.ORGANIZADOR.value)

    ong = MagicMock(spec=Ong)
    ong.id = uuid.uuid4()
    ong.nome = "ONG Teste"
    mock_get.return_value = ong

    mock_instance = mock_repo.return_value
    mock_instance.get_by_ong.return_value = []

    response = client.get(f"/ong/{ong.id}/interesses")

    assert response.status_code == 200
    mock_get.assert_called_once_with(Ong, ong.id)
    mock_instance.get_by_ong.assert_called_once_with(ong.id)