from fastapi import APIRouter, HTTPException

from src.projects.schemas import Project

# - - - - - - - - - - IN-MEMORY DB - - - - - - - - - - #

# Projects
first = Project(id=1, name="first", description="The First project")
second = Project(id=2, name="second", description="The Second project")
third = Project(id=3, name="third", description="The Third project")

# Projects DB
projects_db = {1: first, 2: second, 3: third}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - #

router = APIRouter(prefix="/projects")


@router.get("/")
def read_projects() -> dict[int, Project]:
    """Read all projects"""
    return projects_db


@router.get("/{project_id}/info")
def read_project(project_id: int) -> Project:
    """Read project description"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    return projects_db[project_id]


@router.post("/")
def create_project(project: Project) -> Project:
    """Create new project"""
    if project.id in projects_db:
        raise HTTPException(
            status_code=400, detail=f"Project with {project.id} already exists."
        )

    projects_db[project.id] = project
    return project


@router.put("/{project_id}/info")
def update_project(project_id: int, project: Project) -> Project:
    """Update project"""
    if project_id not in projects_db:
        raise HTTPException(
            status_code=404, detail=f"Project with {project_id} does not exist."
        )

    projects_db[project_id] = project
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int) -> Project:
    """Delete project"""
    if project_id not in projects_db:
        raise HTTPException(
            status_code=404, detail=f"Project with {project_id} does not exist."
        )

    project = projects_db.pop(project_id)
    return project
