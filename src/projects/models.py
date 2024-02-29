from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Project(Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    users = relationship(
        "User", secondary="m2m_projects_users", back_populates="projects"
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    owner = relationship("User")
    logo_id: Mapped[UUID] = mapped_column(ForeignKey("logos.id"), nullable=True)
    logo = relationship("Logo")
    documents = relationship("Document", backref="projects")
