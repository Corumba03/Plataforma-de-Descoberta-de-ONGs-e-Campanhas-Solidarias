import uuid
import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.main.models import db
from app.main.models.campanha import Campanha


class Ong(db.Model):
    __tablename__ = 'ong'

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(255))
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True)
    id_area_atuacao: Mapped[uuid.UUID] = mapped_column(ForeignKey('area_atuacao.id'))
    data_cadastro: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    id_dono: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('usuario.id'))

    area_atuacao: Mapped["AreaAtuacao"] = relationship(back_populates="ongs")
    contatos: Mapped[List["ContatoOng"]] = relationship(back_populates="ong", cascade="all, delete-orphan")
    campanhas: Mapped[List["Campanha"]] = relationship(back_populates="ong", cascade="all, delete-orphan")
    noticias: Mapped[List["Noticia"]] = relationship(back_populates="ong", cascade="all, delete-orphan")
    interesses: Mapped[List["InteresseVoluntariado"]] = relationship(back_populates="ong", cascade="all, delete-orphan")
    dono: Mapped[Optional["Usuario"]] = relationship(back_populates="ongs")

    def to_dict(self) -> dict:
        """Serializa a ONG para representação JSON, incluindo relacionamentos."""
        return {
            "id": str(self.id),
            "nome": self.nome,
            "descricao": self.descricao,
            "cnpj": self.cnpj,
            "area_atuacao": self.area_atuacao.nome_area if self.area_atuacao else None,
            "contatos": [contato.to_dict() for contato in self.contatos],
            "campanhas": [campanha.to_dict() for campanha in self.campanhas],
            "noticias": [noticia.to_dict() for noticia in self.noticias],
            "interesses": [interesse.to_dict() for interesse in self.interesses],
            "dono": self.dono.to_dict() if self.dono else None,
        }
