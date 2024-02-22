from typing import Generator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from src.database import Base, get_db
from src.main import app
from src.projects.models import ProjectORM

TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:3254/test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    yield session
    # After the module, drop all tables in the database
    meta = MetaData()
    meta.reflect(bind=engine)
    for table in reversed(meta.sorted_tables):
        session.execute(delete(table))
    session.commit()
    session.close()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
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
