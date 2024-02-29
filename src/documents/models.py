from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    declared_attr,
    mapped_column,
)

from src.models import Base


class BaseDocument(Base):
    __abstract__ = True
    name: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)

    @declared_attr
    def owner_id(self) -> Mapped[UUID]:
        return mapped_column(ForeignKey("users.id"), nullable=True)


class Document(BaseDocument):
    __tablename__ = "documents"
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=True)


class Logo(BaseDocument):
    __tablename__ = "logos"
