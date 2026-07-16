import datetime
import calendar
from unittest.mock import patch

import jwt
import pytest
from flask import session

from app.main.controllers.auth_controller import SECRET_KEY, generate_token, login_required, organizador_required, validate_token
from app.main.models import Usuario, UserType

from app import create_app
app = create_app()
app.config.update(SECRET_KEY="test-secret-key")

''' Testes para a função generate_token 
1) Testa se a função retorna um token válido para um usuário válido
2) Testa se a função lança um erro para um usuário inválido
3) Testa se o token contém as informações corretas
4) Testa se o token não pode ser decodificado com uma chave incorreta'''

def test_generate_token_valid_input():
    user = Usuario(id=1, tipo=UserType.ORGANIZADOR.value)

    token = generate_token(user)

    assert token is not None


def test_generate_token_invalid_input():
    invalid_user = [1, UserType.ORGANIZADOR.value]

    with pytest.raises(TypeError):
        generate_token(invalid_user)

@pytest.mark.parametrize(
    "user_id,user_tipo",
    [
        (1, UserType.ORGANIZADOR.value),
        (2, UserType.PARTICIPANTE.value),
        (3, UserType.VOLUNTARIO.value),
        (99, UserType.ADMIN.value),
    ],
    ids=[
        UserType.ORGANIZADOR.value,
        UserType.PARTICIPANTE.value,
        UserType.VOLUNTARIO.value,
        UserType.ADMIN.value,
    ],
)

def test_generate_token_valid_token(user_id, user_tipo):
    user = Usuario(id=user_id, tipo=user_tipo)

    token = generate_token(user)

    # Decodifica o token para verificar se contém as informações corretas
    decoded_token = jwt.decode(token, "super-secret", algorithms=["HS256"])

    assert decoded_token["user_id"] == str(user.id)
    assert decoded_token["tipo"] == user.tipo
    assert "exp" in decoded_token  # Verifica se a chave de expiração está presente

def test_generate_token_invalid_token():
    user = Usuario(id=1, tipo=UserType.ORGANIZADOR.value)

    token = generate_token(user)

    # Tenta decodificar o token com uma chave incorreta
    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        jwt.decode(token, "wrong-secret", algorithms=["HS256"])


def test_validate_token_expirado():
    expired_token = jwt.encode(
        {
            "user_id": "1",
            "tipo": UserType.ORGANIZADOR.value,
            "exp": datetime.datetime.utcnow() - datetime.timedelta(seconds=1),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        validate_token(expired_token)

'''Testes para a função login_required
1) Testa se a função redireciona para login quando o usuário não está autenticado
2) Testa se a função permite o acesso quando o usuário está autenticado'''

@login_required
def protected_view():
    return "ok"

def test_login_required_decorator_deny():
    # Usuário não autenticado deve ser redirecionado para login.
    with app.test_request_context("/rota-protegida"):
        response = protected_view()

        assert response.status_code == 302
        assert response.location.endswith("/auth/login")
        assert session.get("_flashes") == [("danger", "Você precisa estar logado")]
    

def test_login_required_decorator_allow():
    # Usuário autenticado deve acessar a view normalmente.
    with app.test_request_context("/rota-protegida"):
        session["user_id"] = "1"

        response = protected_view()

        assert response == "ok"


def test_login_required_decorator_allow_with_bearer_token():
    user = Usuario(id=1, tipo=UserType.ORGANIZADOR.value)
    token = generate_token(user)

    with app.test_request_context("/rota-protegida", headers={"Authorization": f"Bearer {token}"}):
        response = protected_view()

        assert response == "ok"
        assert session.get("user_id") == "1"
        assert session.get("tipo") == UserType.ORGANIZADOR.value

'''Testes para a função organizador_required
1) Testa se a função nega acesso quando o usuário não é organizador
2) Testa se a função permite o acesso quando o usuário é organizador'''

@organizador_required
def organizer_only_view():
    return "ok"


def test_organizador_required_decorator_deny():
    with app.test_request_context("/rota-organizador"):
        session["tipo"] = UserType.PARTICIPANTE.value

        response, status_code = organizer_only_view()

        assert response == "Acesso negado"
        assert status_code == 403


def test_organizador_required_decorator_allow():
    with app.test_request_context("/rota-organizador"):
        session["tipo"] = UserType.ORGANIZADOR.value

        response = organizer_only_view()

        assert response == "ok"


'''Testes para a função register
1) Testa se a função retorna erro quando o usuário já existe
2) Testa se a função cria um novo usuário com sucesso'''

def test_register_user_exists(client):
    # Simula que o usuário já existe
    with patch("app.main.controllers.auth_controller.Usuario.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = Usuario(id=1, email="test@example.com")

        response = client.post("/auth/register", data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha": "password",
            "tipo": UserType.VOLUNTARIO.value
        })

    assert response.status_code == 400
    assert "Usuário já existe" in response.data.decode()

@pytest.mark.parametrize(
    "nome,email,senha,tipo, expected_status",
    [
        ("Valid User", "user@example.com", "password123", UserType.VOLUNTARIO.value, 302),
        ("Valid User", "user2@example.com", "password123", UserType.ORGANIZADOR.value, 302),
        ("", "invalid@example.com", "password", UserType.VOLUNTARIO.value, 400),
        ("No Email", "", "password123", UserType.VOLUNTARIO.value, 400),
        ("Invalid Email", "invalid-email", "password", UserType.VOLUNTARIO.value, 400),
        ("No Password", "nopassword@example.com", "", UserType.VOLUNTARIO.value, 400),
        ("Invalid Tipo", "invalidtipo@example.com", "password", "invalid_tipo", 400),
    ]
)

def test_register_success(client, db, nome, email, senha, tipo, expected_status):
    response = client.post("/auth/register", data={
        "nome": nome,
        "email": email,
        "senha": senha,
        "tipo": tipo
    })

    assert response.status_code == expected_status

    # Verifica se a sessão foi criada corretamente
    if expected_status == 302:
        assert response.location.endswith("/home")
        with client.session_transaction() as sess:
            assert sess.get("user_id") is not None
            assert sess.get("user_nome") == nome
            assert sess.get("tipo") == tipo
    else:
        page = response.data.decode()
        assert "Criar conta" in page


'''Testes para a função login
1) Testa se a função retorna erro quando as credenciais são inválidas
2) Testa se a função cria a sessão corretamente quando as credenciais são válidas'''

@pytest.mark.parametrize(
    "email, senha, user_exists, password_ok, expected_status",
    [
        ("invalid@example.com", "wrongpassword", False, False, 200),
        ("valid@example.com", "correctpassword", True, True, 302),
        ("", "password", False, False, 200),
        ("valid@example.com", "", True, False, 200),
        ("", "", False, False, 200),
        ("valid@example", "wrongpassword", True, False, 200),

    ]
)

def test_login(client, email, senha, user_exists, password_ok, expected_status):
    with patch("app.main.controllers.auth_controller.Usuario.query") as mock_query, \
         patch("app.main.controllers.auth_controller.check_password_hash") as mock_check_hash:
        user = None
        if user_exists:
            user = Usuario(
                id=1,
                nome="Usuário Válido",
                email="valid@example.com",
                senha_hash="hash",
                tipo=UserType.VOLUNTARIO.value,
            )

        mock_query.filter_by.return_value.first.return_value = user
        mock_check_hash.return_value = password_ok

        response = client.post("/auth/login", data={
            "email": email,
            "senha": senha
        })

    assert response.status_code == expected_status
    if expected_status == 302:
        assert response.location.endswith("/home")
        with client.session_transaction() as sess:
            assert sess.get("user_id") is not None
            assert sess.get("user_nome") == "Usuário Válido"
            assert sess.get("tipo") == UserType.VOLUNTARIO.value
    else:
        page = response.data.decode()
        assert "Entrar" in page
        assert "action=\"/auth/login\"" in page