from typing import Generator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import test_db_url
from src.database import get_db
from src.main import app
from src.models import Base
from src.projects.models import ProjectORM

engine = create_engine(test_db_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    session.begin_nested()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def test_data(db: Session) -> Iterator[tuple[str, str, str]]:
    # Create 3 projects
    project1 = ProjectORM(name="first", description="The First Project")
    project2 = ProjectORM(name="second", description="The Second Project")
    project3 = ProjectORM(name="third", description="The Third Project")

    # Add the projects to the session
    db.add(project1)
    db.add(project2)
    db.add(project3)

    # Commit the session to save the projects
    db.commit()

    # Yield the ids of the projects
    yield str(project1.id), str(project2.id), str(project3.id)
