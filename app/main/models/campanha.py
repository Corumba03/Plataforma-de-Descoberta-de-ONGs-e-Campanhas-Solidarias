import uuid
import datetime
from sqlalchemy import String, Text, ForeignKey, Date, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.main.models import db

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
