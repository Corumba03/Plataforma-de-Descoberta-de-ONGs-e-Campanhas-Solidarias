import datetime
import calendar
from unittest.mock import patch

import jwt
import pytest
from flask import session

from app.main.controllers.auth_controller import SECRET_KEY, generate_token, login_required, organizador_required
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

    with pytest.raises(AttributeError):
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

# TODO adicionar teste para verificar tratamento da expiração do token

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


