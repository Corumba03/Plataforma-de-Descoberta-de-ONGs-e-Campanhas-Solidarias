import uuid
from sqlalchemy import String, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.main.models import db

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
