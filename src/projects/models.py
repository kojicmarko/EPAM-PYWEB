from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class ProjectORM(Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
