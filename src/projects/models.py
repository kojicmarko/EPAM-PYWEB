from uuid import uuid4

from sqlalchemy import UUID, Column, String, Text

from src.database import Base


class ProjectORM(Base):
    __tablename__ = "projects"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(40), nullable=False)
    description = Column(Text, nullable=True)
