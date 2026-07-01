import uuid
import datetime
from sqlalchemy import String, ForeignKey, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.main.models import db

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
