from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
"""Fixtures compartilhadas para os testes."""

import pytest
from app import create_app
from app.models import db as _db


class TestConfig:
    """Configuração usada nos testes — banco SQLite em memória."""

    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = "localhost"


@pytest.fixture(scope="session")
def app():
    """Cria a aplicação Flask uma vez por sessão de testes."""
    app = create_app(config_class=TestConfig)
    return app


@pytest.fixture(scope="function")
def client(app):
    """Cliente de teste do Flask para simular requisições HTTP."""
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope="function")
def db(app):
    """Cria as tabelas antes de cada teste e as remove depois."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()
