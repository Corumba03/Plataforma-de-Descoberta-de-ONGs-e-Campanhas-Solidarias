"""
Unidade Testada: InteresseVoluntariadoRepository
Critérios Utilizados:
1. Particionamento em Classes de Equivalência (Equivalence Partitioning)
2. Grafo de Causa-Efeito / Tabela de Decisão (Decision Table)

Classes de Equivalência para o método 'add(id_usuario, id_ong, mensagem)':
- id_usuario:
  * E1 (Válida): ID de um usuário cadastrado no banco.
  * E2 (Inválida): ID de um usuário inexistente no banco.
- id_ong:
  * E3 (Válida): ID de uma ONG cadastrada no banco.
  * E4 (Inválida): ID de uma ONG inexistente no banco.
- mensagem:
  * E5 (Válida): String não nula (mensagem enviada).
  * E6 (Inválida): Valor nulo (None).

Tabela de Decisão:
+------------------------------+--------+--------+--------+--------+
| Condições                    | Caso 1 | Caso 2 | Caso 3 | Caso 4 |
+------------------------------+--------+--------+--------+--------+
| C1: Usuário existe no banco? | Sim    | Não    | Sim    | Sim    |
| C2: ONG existe no banco?     | Sim    | Sim    | Não    | Sim    |
| C3: Mensagem é não nula?     | Sim    | Sim    | Sim    | Não    |
+------------------------------+--------+--------+--------+--------+
| Ações                        |        |        |        |        |
+------------------------------+--------+--------+--------+--------+
| A1: Cria o registro          | X      |        |        |        |
| A2: Lança IntegrityError     |        | X      | X      | X      |
+------------------------------+--------+--------+--------+--------+
"""

import pytest
import uuid
import datetime
from sqlalchemy.exc import IntegrityError
from app.main.models import AreaAtuacao, Ong, Usuario, InteresseVoluntariado
from app.main.repositories import InteresseVoluntariadoRepository


@pytest.fixture()
def area(db):
    """Cria uma área de atuação de teste."""
    a = AreaAtuacao(nome_area="Saúde")
    db.session.add(a)
    db.session.flush()
    return a


@pytest.fixture()
def ong(db, area):
    """Cria uma ONG de teste."""
    o = Ong(nome="ONG Esperança", cnpj="12345678000100", id_area_atuacao=area.id)
    db.session.add(o)
    db.session.flush()
    return o


@pytest.fixture()
def usuario(db):
    """Cria um usuário voluntário de teste."""
    u = Usuario(nome="João Silva", email="joao@gmail.com", senha_hash="xyz", tipo="voluntario")
    db.session.add(u)
    db.session.flush()
    return u


@pytest.fixture()
def repo():
    """Retorna o repositório de interesse de voluntariado."""
    return InteresseVoluntariadoRepository()


class TestInteresseVoluntariadoRepository:

    # ==========================================
    # 1. CLASSES DE EQUIVALÊNCIA PARA O MÉTODO ADD
    # ==========================================

    def test_add_interesse_valido(self, db, repo, usuario, ong):
        """Classes E1 (Usuario Válido), E3 (ONG Válida), E5 (Mensagem Válida).
        Espera-se que o interesse seja criado com sucesso.
        """
        interesse = repo.add(id_usuario=usuario.id, id_ong=ong.id, mensagem="Quero apoiar a causa.")
        assert interesse.id is not None
        assert isinstance(interesse.id, uuid.UUID)
        assert interesse.mensagem == "Quero apoiar a causa."
        assert interesse.id_usuario == usuario.id
        assert interesse.id_ong == ong.id

        # Verifica persistência no banco
        db_interesse = db.session.get(InteresseVoluntariado, interesse.id)
        assert db_interesse is not None
        assert db_interesse.mensagem == "Quero apoiar a causa."

    def test_add_interesse_usuario_inexistente(self, db, repo, ong):
        """Classe E2 (Usuario Inexistente/Inválido).
        Espera-se violação de FK e falha com IntegrityError.
        """
        non_existent_user_id = uuid.uuid4()
        with pytest.raises(IntegrityError):
            repo.add(id_usuario=non_existent_user_id, id_ong=ong.id, mensagem="Quero ajudar.")
            db.session.commit()

    def test_add_interesse_ong_inexistente(self, db, repo, usuario):
        """Classe E4 (ONG Inexistente/Inválida).
        Espera-se violação de FK e falha com IntegrityError.
        """
        non_existent_ong_id = uuid.uuid4()
        with pytest.raises(IntegrityError):
            repo.add(id_usuario=usuario.id, id_ong=non_existent_ong_id, mensagem="Quero ajudar.")
            db.session.commit()

    def test_add_interesse_mensagem_null(self, db, repo, usuario, ong):
        """Classe E6 (Mensagem Null/Inválida).
        Espera-se que a coluna nullable=False lance um IntegrityError.
        """
        with pytest.raises(IntegrityError):
            repo.add(id_usuario=usuario.id, id_ong=ong.id, mensagem=None)
            db.session.commit()

    # ==========================================
    # 2. CASOS DE TESTE DOS MÉTODOS DE BUSCA (GET)
    # ==========================================

    def test_get_by_usuario_ordem_e_filtro(self, db, repo, usuario, ong):
        """Verifica se busca por usuário retorna corretamente apenas registros dele,
        ordenados de forma decrescente pela data de envio.
        """
        i1 = repo.add(id_usuario=usuario.id, id_ong=ong.id, mensagem="Primeiro contato")
        i2 = repo.add(id_usuario=usuario.id, id_ong=ong.id, mensagem="Segundo contato")

        # Ajusta data_envio manualmente para garantir a ordem cronológica nos testes
        i1.data_envio = datetime.datetime.now() - datetime.timedelta(seconds=10)
        i2.data_envio = datetime.datetime.now()
        db.session.commit()

        interesses = repo.get_by_usuario(usuario.id)
        assert len(interesses) == 2
        # Mais recente primeiro
        assert interesses[0].id == i2.id
        assert interesses[1].id == i1.id

    def test_get_by_ong_ordem_e_filtro(self, db, repo, usuario, ong):
        """Verifica se busca por ONG retorna corretamente apenas registros associados àquela ONG,
        ordenados de forma decrescente pela data de envio.
        """
        usuario2 = Usuario(nome="Maria", email="maria@gmail.com", senha_hash="xyz", tipo="voluntario")
        db.session.add(usuario2)
        db.session.flush()

        i1 = repo.add(id_usuario=usuario.id, id_ong=ong.id, mensagem="João interessado")
        i2 = repo.add(id_usuario=usuario2.id, id_ong=ong.id, mensagem="Maria interessada")

        # Ajusta data_envio manualmente para garantir a ordem cronológica nos testes
        i1.data_envio = datetime.datetime.now() - datetime.timedelta(seconds=10)
        i2.data_envio = datetime.datetime.now()
        db.session.commit()

        interesses = repo.get_by_ong(ong.id)
        assert len(interesses) == 2
        # Mais recente primeiro
        assert interesses[0].id == i2.id
        assert interesses[1].id == i1.id
