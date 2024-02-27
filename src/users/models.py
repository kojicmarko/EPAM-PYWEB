from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    projects = relationship(
        "Project", secondary="m2m_projects_users", back_populates="users"
    )
