import datetime
import calendar
from unittest.mock import patch

import jwt
import pytest

from app.main.controllers.auth_controller import SECRET_KEY, generate_token
from app.main.models import Usuario

''' Testes para a função generate_token 
1) Testa se a função retorna um token válido para um usuário válido
2) Testa se a função lança um erro para um usuário inválido
3) Testa se o token contém as informações corretas
4) Testa se o token não pode ser decodificado com uma chave incorreta'''

def test_generate_token_valid_input():
    user = Usuario(id=1, tipo="organizador")

    token = generate_token(user)

    assert token is not None


def test_generate_token_invalid_input():
    invalid_user = [1, "organizador"]

    with pytest.raises(AttributeError):
        generate_token(invalid_user)

@pytest.mark.parametrize(
    "user_id,user_tipo",
    [
        (1, "organizador"),
        (2, "participante"),
        (3, "voluntario"),
        (99, "admin"),
    ],
    ids=[
        "organizador",
        "participante",
        "voluntario",
        "admin",
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
    user = Usuario(id=1, tipo="organizador")

    token = generate_token(user)

    # Tenta decodificar o token com uma chave incorreta
    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        jwt.decode(token, "wrong-secret", algorithms=["HS256"])

# TODO adicionar teste para verificar tratamento da expiração do token


