# Menmo

menmo.ai

## Backend service

The backend is a FastAPI application with persistence powered by SQLAlchemy. It
exposes endpoints for managing user profiles, ingesting grants, and returning
ranked matches.

### Prerequisites

- Python 3.11+
- (Optional) PostgreSQL 14+ if you do not want to use the default SQLite
  database.

### Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the API locally

```bash
export DATABASE_URL=sqlite:///./app.db  # or your PostgreSQL connection string
uvicorn backend.main:app --reload
```

When running with PostgreSQL ensure the target database already exists. The
application will create the necessary tables on startup.

### Tests

```bash
cd backend
pytest
```

## Matching logic

`backend/matching.py` implements a lightweight AI-inspired matcher. The module
embeds user and grant text into sparse vectors and compares them with cosine
similarity to provide ranked grant recommendations. Unit tests covering the core
matching behaviour live in `backend/tests/`.

## Frontend client

The frontend is a lightweight Next.js project that consumes the backend API.
Pages are available for onboarding, browsing grants, and requesting
recommendations.

### Prerequisites

- Node.js 18+
- pnpm, npm, or yarn

### Installation and development server

```bash
cd frontend
npm install
npm run dev
```

By default the client talks to `http://localhost:8000`. To change this set the
`NEXT_PUBLIC_BACKEND_URL` environment variable before running the dev server.

## Project structure

```
backend/
  main.py          # FastAPI application and route definitions
  db.py            # SQLAlchemy configuration
  models.py        # ORM models
  matching.py      # Matching engine
  tests/           # Pytest test suite
frontend/
  src/pages/       # Next.js pages for the Menmo app
  src/components/  # Shared UI components
  src/lib/         # API helper utilities
```
