from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Document(Base):
    __tablename__ = "documents"
    name: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    owner = relationship("User")
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project = relationship("Project")
