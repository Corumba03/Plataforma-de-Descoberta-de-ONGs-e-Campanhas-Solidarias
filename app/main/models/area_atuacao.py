import uuid
from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.main.models import db

class AreaAtuacao(db.Model):
    __tablename__ = 'area_atuacao'
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_area: Mapped[str] = mapped_column(String(100))
    
    ongs: Mapped[List["Ong"]] = relationship(back_populates="area_atuacao")
