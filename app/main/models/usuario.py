import uuid
from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.main.models import db

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    interesses: Mapped[List["InteresseVoluntariado"]] = relationship(back_populates="usuario")
    ongs: Mapped[List["Ong"]] = relationship(back_populates="dono")

    def to_dict(self):
        return {
            'id': str(self.id),
            'nome': self.nome,
            'email': self.email,
            'tipo': self.tipo
        }