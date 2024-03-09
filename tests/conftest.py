from datetime import timedelta
from io import BytesIO
from typing import Callable, Generator

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings
from src.database import get_db
from src.documents import service as doc_service
from src.documents.schemas import Document
from src.main import app
from src.models import Base
from src.projects import service as project_service
from src.projects.schemas import Project, ProjectCreate
from src.users.auth import service as auth_service
from src.users.schemas import User, UserCreate
from src.utils.auth import create_token
from src.utils.aws.s3 import S3Client

s3 = S3Client()

engine = create_engine(settings.DATABASE_URL)
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
    yield session
    session.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def test_projects(db: Session, test_user: User) -> list[Project]:
    projects = [ProjectCreate(name=f"project{i}") for i in range(3)]
    return [project_service.create(project, test_user.id, db) for project in projects]


@pytest.fixture(scope="function", autouse=True)
def truncate_tables(db: Session) -> None:
    db.execute(text("SET session_replication_role = replica;"))

    tables_to_truncate = [
        "users",
        "projects",
        "m2m_projects_users",
        "documents",
        "logos",
    ]
    for table_name in tables_to_truncate:
        db.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
    db.commit()

    db.execute(text("SET session_replication_role = default;"))


@pytest.fixture(scope="function")
def mock_upload_file() -> UploadFile:
    mock_file = BytesIO(b"file content")
    mock_file.name = "mock_file.pdf"
    return UploadFile(file=mock_file)


@pytest.fixture(scope="function")
def test_documents(
    db: Session, test_user: User, test_projects: list[Project]
) -> Generator[list[Document], None, None]:
    project = test_projects[0]
    files = [
        UploadFile(file=BytesIO(b"file content"), filename=f"document{i}")
        for i in range(3)
    ]
    documents = [file.filename for file in files if file.filename]
    yield [
        doc_service.create(
            file,
            project,
            test_user,
            db,
        )
        for file in files
    ]
    for doc_name in documents:
        s3.delete(f"{project.id}_{doc_name}", "documents")


# USERS:
@pytest.fixture
def user_factory(db: Session) -> Callable[..., User]:
    def _create_user(username: str) -> User:
        user_create = UserCreate(username=username, password="12345678")
        return auth_service.create(user_create, db)

    return _create_user


@pytest.fixture(scope="function")
def test_user(user_factory: Callable[..., User]) -> User:
    return user_factory("test")


@pytest.fixture(scope="function")
def unauthorized_user(user_factory: Callable[..., User]) -> User:
    return user_factory("unauthorized")


@pytest.fixture(scope="function")
def invited_user(user_factory: Callable[..., User]) -> User:
    return user_factory("invited")


@pytest.fixture
def participant_user(user_factory: Callable[..., User]) -> User:
    return user_factory("participant")


# TOKENS:
@pytest.fixture
def token_factory() -> Callable[..., str]:
    def _create_token(user: User) -> str:
        token_expires = timedelta(minutes=30)
        token = create_token(
            data={"username": user.username, "id": str(user.id)},
            expires_delta=token_expires,
        )
        return token

    return _create_token


@pytest.fixture(scope="function")
def test_token(token_factory: Callable[..., str], test_user: User) -> str:
    return token_factory(test_user)


@pytest.fixture(scope="function")
def unauthorized_token(
    token_factory: Callable[..., str], unauthorized_user: User
) -> str:
    return token_factory(unauthorized_user)


@pytest.fixture
def participant_token(token_factory: Callable[..., str], participant_user: User) -> str:
    return token_factory(participant_user)
