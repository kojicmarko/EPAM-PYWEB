from uuid import UUID

from sqlalchemy.orm import Session

from src.models import ProjectUser
from src.projects import models as proj_models
from src.projects import schemas
from src.users import models as user_models


def get_by_id(proj_id: UUID, db: Session) -> proj_models.Project | None:
    return (
        db.query(proj_models.Project).filter(proj_models.Project.id == proj_id).first()
    )


def read_all(user_id: UUID, db: Session) -> list[schemas.Project]:
    proj_list_orm = (
        db.query(proj_models.Project)
        .join(ProjectUser)
        .filter(ProjectUser.user_id == user_id)
        .all()
    )
    return [schemas.Project.model_validate(proj) for proj in proj_list_orm]


def read(proj_id: UUID, user_id: UUID, db: Session) -> schemas.Project | None:
    proj_orm = get_by_id(proj_id, db)

    if not proj_orm:
        return None

    project_user = (
        db.query(ProjectUser).filter_by(user_id=user_id, project_id=proj_id).first()
    )

    if not project_user:
        return None

    return schemas.Project.model_validate(proj_orm)


def create(
    proj_create: schemas.ProjectCreate, user_id: UUID, db: Session
) -> schemas.Project:
    proj_orm = proj_models.Project(**proj_create.model_dump(), owner_id=user_id)
    db.add(proj_orm)
    db.commit()

    m2m_relationship = ProjectUser(user_id=user_id, project_id=proj_orm.id)
    db.add(m2m_relationship)
    db.commit()
    return schemas.Project.model_validate(proj_orm)


def update(
    proj_id: UUID, proj_update: schemas.ProjectUpdate, user_id: UUID, db: Session
) -> schemas.Project | None:
    proj_orm = get_by_id(proj_id, db)

    if not proj_orm:
        return None

    project_user = (
        db.query(ProjectUser).filter_by(user_id=user_id, project_id=proj_id).first()
    )
    if not project_user:
        return None

    if proj_update.name is not None and proj_update.name != proj_orm.name:
        proj_orm.name = proj_update.name

    if (
        proj_update.description is not None
        and proj_update.description != proj_orm.description
    ):
        proj_orm.description = proj_update.description

    db.commit()
    return schemas.Project.model_validate(proj_orm)


def delete(proj_id: UUID, user_id: UUID, db: Session) -> bool:
    proj_orm = get_by_id(proj_id, db)

    if not proj_orm or proj_orm.owner_id != user_id:
        return False

    db.delete(proj_orm)
    db.commit()
    return True


def invite(proj_id: UUID, username: str, owner_id: UUID, db: Session) -> bool:
    proj_orm = get_by_id(proj_id, db)

    if not proj_orm or proj_orm.owner_id != owner_id:
        return False

    user_to_invite = (
        db.query(user_models.User).filter(user_models.User.username == username).first()
    )
    if not user_to_invite:
        return False

    m2m_relationship = ProjectUser(user_id=user_to_invite.id, project_id=proj_orm.id)
    db.add(m2m_relationship)
    db.commit()

    return True
