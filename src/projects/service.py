from typing import Literal
from uuid import UUID

from sqlalchemy.orm import Session

from src.projects.models import ProjectORM
from src.projects.schemas import Project, ProjectCreate, ProjectUpdate


def get_by_id(proj_id: str, db: Session) -> ProjectORM | None:
    try:
        UUID(proj_id, version=4)
    except ValueError:
        return None

    return db.query(ProjectORM).filter(ProjectORM.id == proj_id).first()


def read_all(db: Session) -> list[Project]:
    proj_list_orm = db.query(ProjectORM).all()
    return [Project.model_validate(proj) for proj in proj_list_orm]


def read(proj_id: str, db: Session) -> Project | None:
    proj_orm = get_by_id(proj_id, db)

    if not proj_orm:
        return None

    return Project.model_validate(proj_orm)


def create(proj_create: ProjectCreate, db: Session) -> Project:
    proj_orm = ProjectORM(**proj_create.model_dump())
    db.add(proj_orm)
    db.commit()
    return Project.model_validate(proj_orm)


def update(proj_id: str, proj_update: ProjectUpdate, db: Session) -> Project | None:
    proj_orm = get_by_id(proj_id, db)

    if not proj_orm:
        return None

    if proj_update.name is not None and proj_update.name != proj_orm.name:
        proj_orm.name = proj_update.name

    if (
        proj_update.description is not None
        and proj_update.description != proj_orm.description
    ):
        proj_orm.description = proj_update.description

    db.commit()
    return Project.model_validate(proj_orm)


def delete(proj_id: str, db: Session) -> Literal[True] | Literal[False]:
    proj_orm = get_by_id(proj_id, db)

    if not proj_orm:
        return False

    db.delete(proj_orm)
    db.commit()
    return True
