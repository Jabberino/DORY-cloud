# DORY Cloud API

Cloud backend for the DORY swim training app with lap/stroke detection ML pipeline.

## Quick Start (Docker)

```bash
docker-compose up -d
docker-compose exec api alembic upgrade head
open http://localhost:8000/docs
```

## Manual Deployment (No Docker)

```bash
# 1. Install PostgreSQL and create database
sudo -u postgres createdb swimdb
sudo -u postgres createuser swimuser -P

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# 4. Run migrations
alembic upgrade head

# 5. Start server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Tech Stack

- **FastAPI** - API framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Alembic** - Migrations

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

