import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import db as _db


@pytest.fixture()
def app():
    """Cria a aplicação Flask com configs exclusivas de teste."""
    app = create_app()
    
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SERVER_NAME="localhost"
    )
    return app


@pytest.fixture()
def client(app):
    """Cliente de teste do Flask para simular requisições HTTP."""
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture()
def db(app):
    """Cria as tabelas em memória antes do teste e limpa depois."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()
