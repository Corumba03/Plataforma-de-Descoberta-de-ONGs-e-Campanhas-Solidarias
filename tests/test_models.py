"""Testes unitários para os modelos do banco de dados."""

import uuid
from datetime import date, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import AreaAtuacao, Campanha, ContatoOng, Noticia, Ong, Usuario


@pytest.fixture()
def area(db):
    """Cria uma área de atuação padrão."""
    a = AreaAtuacao(nome_area="Educação")
    db.session.add(a)
    db.session.flush()
    return a


@pytest.fixture()
def ong(db, area):
    """Cria uma ONG padrão vinculada à área."""
    o = Ong(nome="ONG Teste", cnpj="12345678000199", id_area_atuacao=area.id)
    db.session.add(o)
    db.session.flush()
    return o


class TestAreaAtuacao:

    def test_criar_com_uuid(self, db):
        area = AreaAtuacao(nome_area="Saúde")
        db.session.add(area)
        db.session.commit()

        assert isinstance(area.id, uuid.UUID)
        assert area.nome_area == "Saúde"

    def test_relacao_com_ongs(self, db, area):
        ong = Ong(nome="Verde", cnpj="11111111000111", id_area_atuacao=area.id)
        db.session.add(ong)
        db.session.commit()

        assert len(area.ongs) == 1
        assert area.ongs[0].nome == "Verde"


class TestOng:

    def test_criar_com_uuid(self, db, area):
        ong = Ong(nome="Instituto", cnpj="22222222000100", id_area_atuacao=area.id)
        db.session.add(ong)
        db.session.commit()

        assert isinstance(ong.id, uuid.UUID)
        assert ong.nome == "Instituto"

    def test_descricao_opcional(self, db, area):
        ong = Ong(nome="Sem Desc", cnpj="33333333000100", id_area_atuacao=area.id)
        db.session.add(ong)
        db.session.commit()

        assert ong.descricao is None

    def test_cnpj_unico(self, db, area):
        db.session.add(Ong(nome="A", cnpj="44444444000100", id_area_atuacao=area.id))
        db.session.commit()

        db.session.add(Ong(nome="B", cnpj="44444444000100", id_area_atuacao=area.id))
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_relacao_area_atuacao(self, db, ong):
        assert ong.area_atuacao.nome_area == "Educação"

    def test_relacoes_vazias_inicialmente(self, db, ong):
        db.session.commit()
        assert ong.contatos == []
        assert ong.campanhas == []
        assert ong.noticias == []

    def test_data_cadastro_gerada_automaticamente(self, db, area):
        ong = Ong(nome="Com Data", cnpj="55555555000100", id_area_atuacao=area.id)
        db.session.add(ong)
        db.session.commit()

        assert isinstance(ong.data_cadastro, datetime)

    def test_area_atuacao_obrigatoria(self, db):
        db.session.add(Ong(nome="Sem Area", cnpj="66666666000100", id_area_atuacao=None))
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_area_atuacao_inexistente(self, db):
        db.session.add(Ong(nome="Area Inexistente", cnpj="77777777000100", id_area_atuacao=uuid.uuid4()))
        with pytest.raises(IntegrityError):
            db.session.commit()


class TestContatoOng:

    def test_criar_e_relacao(self, db, ong):
        c = ContatoOng(tipo_contato="Email", valor="a@b.com", id_ong=ong.id)
        db.session.add(c)
        db.session.commit()

        assert isinstance(c.id, uuid.UUID)
        assert c.ong.nome == "ONG Teste"
        assert len(ong.contatos) == 1

    def test_ong_obrigatoria(self, db):
        db.session.add(ContatoOng(tipo_contato="Email", valor="x@y.com", id_ong=None))
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_ong_inexistente(self, db):
        db.session.add(ContatoOng(tipo_contato="Email", valor="x@y.com", id_ong=uuid.uuid4()))
        with pytest.raises(IntegrityError):
            db.session.commit()


class TestCampanha:

    def test_criar_com_status_padrao(self, db, ong):
        c = Campanha(titulo="Camp", id_ong=ong.id)
        db.session.add(c)
        db.session.commit()

        assert isinstance(c.id, uuid.UUID)
        assert c.status == "ativa"
        assert c.data_inicio is None
        assert c.descricao is None

    def test_com_datas_e_descricao(self, db, ong):
        c = Campanha(
            titulo="Completa",
            status="inativa",
            data_inicio=date(2026, 1, 1),
            data_fim=date(2026, 12, 31),
            descricao="Desc",
            id_ong=ong.id,
        )
        db.session.add(c)
        db.session.commit()

        assert c.status == "inativa"
        assert c.data_inicio == date(2026, 1, 1)
        assert c.ong.nome == "ONG Teste"

    def test_ong_obrigatoria(self, db):
        db.session.add(Campanha(titulo="Sem ONG", id_ong=None))
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_ong_inexistente(self, db):
        db.session.add(Campanha(titulo="ONG Inexistente", id_ong=uuid.uuid4()))
        with pytest.raises(IntegrityError):
            db.session.commit()


class TestNoticia:

    def test_criar_com_link_opcional(self, db, ong):
        n = Noticia(titulo="Notícia", id_ong=ong.id)
        db.session.add(n)
        db.session.commit()

        assert isinstance(n.id, uuid.UUID)
        assert n.link is None
        assert n.ong.nome == "ONG Teste"

    def test_com_link(self, db, ong):
        n = Noticia(titulo="Com Link", link="https://ex.org", id_ong=ong.id)
        db.session.add(n)
        db.session.commit()

        assert n.link == "https://ex.org"

    def test_data_publicacao_gerada_automaticamente(self, db, ong):
        n = Noticia(titulo="Com Data", id_ong=ong.id)
        db.session.add(n)
        db.session.commit()

        assert isinstance(n.data_publicacao, datetime)

    def test_ong_obrigatoria(self, db):
        db.session.add(Noticia(titulo="Sem ONG", id_ong=None))
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_ong_inexistente(self, db):
        db.session.add(Noticia(titulo="ONG Inexistente", id_ong=uuid.uuid4()))
        with pytest.raises(IntegrityError):
            db.session.commit()


class TestUsuario:

    def test_criar_usuario_com_uuid(self, db):
        user = Usuario(
            nome="Maria",
            email="maria@exemplo.org",
            senha_hash="hash-seguro",
            tipo="usuario",
        )
        db.session.add(user)
        db.session.commit()

        assert isinstance(user.id, uuid.UUID)
        assert user.nome == "Maria"
        assert user.email == "maria@exemplo.org"
        assert user.tipo == "usuario"

    def test_email_unico(self, db):
        db.session.add(
            Usuario(
                nome="A",
                email="repetido@exemplo.org",
                senha_hash="hash-a",
                tipo="usuario",
            )
        )
        db.session.commit()

        db.session.add(
            Usuario(
                nome="B",
                email="repetido@exemplo.org",
                senha_hash="hash-b",
                tipo="organizador",
            )
        )
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_tipo_obrigatorio(self, db):
        db.session.add(
            Usuario(
                nome="Sem Tipo",
                email="semtipo@exemplo.org",
                senha_hash="hash",
                tipo=None,
            )
        )
        with pytest.raises(IntegrityError):
            db.session.commit()
