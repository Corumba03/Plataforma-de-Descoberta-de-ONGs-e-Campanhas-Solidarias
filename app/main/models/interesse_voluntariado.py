import uuid
import datetime
from sqlalchemy import Text, ForeignKey, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.main.models import db


class InteresseVoluntariado(db.Model):
    __tablename__ = 'interesse_voluntariado'

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario: Mapped[uuid.UUID] = mapped_column(ForeignKey('usuario.id'), nullable=False)
    id_ong: Mapped[uuid.UUID] = mapped_column(ForeignKey('ong.id'), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    data_envio: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())

    usuario: Mapped["Usuario"] = relationship(back_populates="interesses")
    ong: Mapped["Ong"] = relationship(back_populates="interesses")
