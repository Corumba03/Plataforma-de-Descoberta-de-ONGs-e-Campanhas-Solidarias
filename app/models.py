from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
from sqlalchemy import String, Text, ForeignKey, Date, DateTime, func, Uuid
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
