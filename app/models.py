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
    id_dono: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('usuario.id'))

    area_atuacao: Mapped["AreaAtuacao"] = relationship(back_populates="ongs")
    contatos: Mapped[List["ContatoOng"]] = relationship(back_populates="ong", cascade="all, delete-orphan")
    campanhas: Mapped[List["Campanha"]] = relationship(back_populates="ong", cascade="all, delete-orphan")
    noticias: Mapped[List["Noticia"]] = relationship(back_populates="ong", cascade="all, delete-orphan")
    interesses: Mapped[List["InteresseVoluntariado"]] = relationship(back_populates="ong", cascade="all, delete-orphan")
    dono: Mapped[Optional["Usuario"]] = relationship(back_populates="ongs")

class ContatoOng(db.Model):
    __tablename__ = 'contato_ong'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_contato: Mapped[str] = mapped_column(String(50))
    valor: Mapped[str] = mapped_column(String(255))
    id_ong: Mapped[uuid.UUID] = mapped_column(ForeignKey('ong.id'))

    ong: Mapped["Ong"] = relationship(back_populates="contatos")

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

class Noticia(db.Model):
    __tablename__ = 'noticia'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_ong: Mapped[uuid.UUID] = mapped_column(ForeignKey('ong.id'))
    titulo: Mapped[str] = mapped_column(String(200))
    data_publicacao: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    link: Mapped[Optional[str]] = mapped_column(String)
    
    ong: Mapped["Ong"] = relationship(back_populates="noticias")

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    interesses: Mapped[List["InteresseVoluntariado"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    ongs: Mapped[List["Ong"]] = relationship(back_populates="dono", cascade="all, delete-orphan")

class InteresseVoluntariado(db.Model):
    __tablename__ = 'interesse_voluntariado'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario: Mapped[uuid.UUID] = mapped_column(ForeignKey('usuario.id'), nullable=False)
    id_ong: Mapped[uuid.UUID] = mapped_column(ForeignKey('ong.id'), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    data_envio: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    usuario: Mapped["Usuario"] = relationship(back_populates="interesses")
    ong: Mapped["Ong"] = relationship(back_populates="interesses")