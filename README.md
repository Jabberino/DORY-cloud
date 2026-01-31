# DORY Cloud API

Cloud backend for the DORY swim training app with lap/stroke detection ML pipeline.

## Quick Start

```bash
# Start PostgreSQL + API
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Access API docs
open http://localhost:8000/docs
```

## Tech Stack

- **FastAPI** - API framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Alembic** - Migrations
- **Docker Compose** - Deployment

## API Endpoints

| Resource | Endpoints |
|----------|-----------|
| Teams | `POST /teams`, `GET /teams/{id}`, `DELETE /teams/{id}` |
| Coaches | `POST /coaches`, `GET /coaches/{id}` |
| Swimmers | `POST /swimmers`, `GET/PUT /swimmers/{id}` |
| Exercises | `POST/GET /teams/{id}/exercises` |
| Sessions | `POST /sessions`, `POST /sessions/{id}/process` |
| Goals | `POST /swimmers/{id}/goals`, `GET /goals/{id}` |

## ML Pipeline

Upload sensor data via `POST /sessions`, then call `POST /sessions/{id}/process` to run lap/stroke detection.
