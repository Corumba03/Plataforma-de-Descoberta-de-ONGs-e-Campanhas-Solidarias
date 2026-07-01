from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
from sqlalchemy import Enum, String, Text, ForeignKey, Date, DateTime, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

db = SQLAlchemy()

class AreaAtuacao(db.Model):
    __tablename__ = 'area_atuacao'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_area: Mapped[str] = mapped_column(String(100))
    
    ongs: Mapped[List["Ong"]] = relationship(back_populates="area_atuacao")

class Ong(db.Model):
    __tablename__ = 'ong'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(255))
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True)
    id_area_atuacao: Mapped[uuid.UUID] = mapped_column(ForeignKey('area_atuacao.id'))
    data_cadastro: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    area_atuacao: Mapped["AreaAtuacao"] = relationship(back_populates="ongs")
    contatos: Mapped[List["ContatoOng"]] = relationship(back_populates="ong")
    campanhas: Mapped[List["Campanha"]] = relationship(back_populates="ong")
    noticias: Mapped[List["Noticia"]] = relationship(back_populates="ong")
    interesses: Mapped[List["InteresseVoluntariado"]] = relationship(back_populates="ong")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "nome": self.nome,
            "descricao": self.descricao,
            "cnpj": self.cnpj,
            "area_atuacao": self.area_atuacao.nome_area if self.area_atuacao else None,
            "contatos": [contato.to_dict() for contato in self.contatos],
            "campanhas": [campanha.to_dict() for campanha in self.campanhas],
            "noticias": [noticia.to_dict() for noticia in self.noticias]
        }

class ContatoOng(db.Model):
    __tablename__ = 'contato_ong'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_contato: Mapped[str] = mapped_column(String(50))
    valor: Mapped[str] = mapped_column(String(255))
    id_ong: Mapped[uuid.UUID] = mapped_column(ForeignKey('ong.id'))

    ong: Mapped["Ong"] = relationship(back_populates="contatos")

    def to_dict(self):
        return {
            "id": str(self.id),
            "tipo": self.tipo_contato,
            "valor": self.valor
        }

class Campanha(db.Model):
    __tablename__ = 'campanha'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_ong: Mapped[uuid.UUID] = mapped_column(ForeignKey('ong.id'))
    titulo: Mapped[str] = mapped_column(String(200))
    status: Mapped[Optional[str]] = mapped_column(String(20), default='ativa')
    data_inicio: Mapped[Optional[datetime.date]] = mapped_column(Date)
    data_fim: Mapped[Optional[datetime.date]] = mapped_column(Date)
    descricao: Mapped[Optional[str]] = mapped_column(Text)

    ong: Mapped["Ong"] = relationship(back_populates="campanhas")

    def to_dict(self, include_ong=False):
        data = {
            "id": str(self.id),
            "titulo": self.titulo,
            "descricao": self.descricao,
            "status": self.status,
            "data_inicio": self.data_inicio.isoformat() if self.data_inicio else None,
            "data_fim": self.data_fim.isoformat() if self.data_fim else None,
        }
        if include_ong and self.ong:
            data["ong"] = {
                "id": str(self.ong.id),
                "nome": self.ong.nome
            }
        return data

class Noticia(db.Model):
    __tablename__ = 'noticia'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_ong: Mapped[uuid.UUID] = mapped_column(ForeignKey('ong.id'))
    titulo: Mapped[str] = mapped_column(String(200))
    data_publicacao: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    link: Mapped[Optional[str]] = mapped_column(String)
    
    ong: Mapped["Ong"] = relationship(back_populates="noticias")

    def to_dict(self):
        return {
            "id": str(self.id),
            "titulo": self.titulo,
            "data_publicacao": self.data_publicacao.isoformat() if self.data_publicacao else None,
            "link": self.link
        }

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    interesses: Mapped[List["InteresseVoluntariado"]] = relationship(back_populates="usuario")

class InteresseVoluntariado(db.Model):
    __tablename__ = 'interesse_voluntariado'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario: Mapped[uuid.UUID] = mapped_column(ForeignKey('usuario.id'), nullable=False)
    id_ong: Mapped[uuid.UUID] = mapped_column(ForeignKey('ong.id'), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    data_envio: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    usuario: Mapped["Usuario"] = relationship(back_populates="interesses")
    ong: Mapped["Ong"] = relationship(back_populates="interesses")