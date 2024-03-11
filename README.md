# FINAL-PYWEB

## Description

This is a project management dashboard API built with FastAPI. It allows users to create, update, share, and delete project information.

## Getting Started

### Prerequisites

- Python 3.10.6
- Poetry for dependency management
- Make for the Makefile
- Docker (for building and running the application in a container)
- PostgreSQL 15

### Installation

1. Clone the repository:
```commandline
git clone git@github.com:kojicmarko/FINAL-PYWEB.git
```
2. Navigate to project directory:
```commandline
cd FINAL-PYWEB
```
3. Install dependencies:
```commandline
make install
```

## Setting up Environment Variables
Before running the application, you need to set up the necessary environment variables.

These include:
- `SECRET_KEY`
- `ALGORITHM`
- `TOKEN_EXPIRE_TIME`
- `DATABASE_URL`
- `DB_HOST`
- `DB_PORT`
- `AWS_BUCKET_NAME`
- `AWS_DEFAULT_REGION`

You can set these up in a `.env` file in the root of your project directory.

## Setting Up the Database

This application uses PostgreSQL 15. Make sure you have it installed and create a new database for this application.

## Running Alembic Migrations

After setting up the database, you need to run Alembic migrations to create the necessary tables:
```commandline
make migrations
```

## Running the Application Locally
1.  Start the server directly:
```commandline
make run
```
## Running the Application inside Docker
1. Build the Docker image:
```commandline
make build
```
2. Start a Docker container with the server:
```commandline
make up-docker
```
3. To stop the Docker container and preserve volumes:
```commandline
make down-docker
```
4. To stop the Docker container and delete volumes:
```commandline
make down-docker-v
```

## Linting
1. Lint and fix style and lint type-hinting:
```commandline
make lint
```

## Testing
1. Run tests:
```commandline
make test
```

## API Endpoints

The API provides the following endpoints:

### Users/Auth

- `POST /auth`: Creates a user.
- `POST /login`: Logs in the user.

### Projects

- `POST /projects`: Creates a new project. Making the user who created it the project owner
- `GET /projects`: Returns all projects where user is a participant.
- `GET /project/<project_id>/info`: Returns project information, if the user is a participant.
- `PUT /project/<project_id>/info`: Updates project information, if the user is a participant.
- `DELETE /project/<project_id>`: Deletes project, if the user is project owner. 
- `POST /project/<project_id>/invite?user=<username>`: Adds user to a project as a participant. Only the project owner can invite.

### Documents

- `GET /project/<project_id>/documents`: Returns all documents of a project.
- `POST /project/<project_id>/documents`: Uploads a document for a specific project.
- `GET /document/<document_id>`: Returns a document.
- `PUT /document/<document_id>`: Updates a document.
- `DELETE /document/<document_id>`: Deletes a document, if the user is project owner.

### Logos

- `GET /project/<project_id>/logo`: Returns the logo of a project.
- `PUT /project/<project_id>/logo`: Updates the logo of a project.
- `DELETE /project/<project_id>/logo`: Deletes the logo, if the user is project owner.