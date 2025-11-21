# Menmo

This repository contains an opinionated prototype of **Menmo’s climate grant copilot** with a FastAPI backend and a React front-end. The backend models the end-to-end customer journey described in the Menmo product brief – from the 2 minute eligibility quick scan to the RAG-guided application builder, evidence validation, deadline radar and post-submission insights.

## Backend

The backend service lives in [`backend/`](backend/) and exposes REST APIs for managing user profiles, ingesting grant opportunities and generating AI-assisted matches.

### Features

- **Multi-stage Journey API** – `/journey/*` endpoints cover Quick Scan, Funding Match, Gap-to-Yes planner, Application Builder, Evidence AutoCheck, Deadline Radar, Finalisation, and Post Submission updates.
- **Rules- + RAG-driven intelligence** – grants include structured rules JSON alongside proprietary notes; the `backend/rag.py` utility retrieves highlighted knowledge snippets (from [`backend/data/documents.json`](backend/data/documents.json)) to ground explanations and AI-generated drafts.
- **Rich persistence model** – SQLAlchemy models track user profiles, project payloads, stored matches (with reasons/blockers/citations), remediation tasks, application sections, evidence statuses, and deadlines.
- **Optional Supabase replication** – configure credentials to mirror matches and remediation tasks into Supabase tables for analytics or downstream automation.
- **Open-data scraping utilities** – harvests climate-related grant catalogues from CKAN portals (Data.gov, data.ca.gov) and normalises them into the Menmo database and RAG corpus.
- **Hybrid matching engine** – `backend/matching.py` prefers `sentence-transformers` embeddings but automatically falls back to a deterministic TF-IDF encoder for offline environments.
- **Comprehensive tests** – Pytest suites assert the full customer journey flow plus low-level matching behaviour.

### Setup

1. Create and activate a Python 3.11 (or newer) virtual environment.
2. Install dependencies (a local virtual environment is recommended):

   ```bash
   pip install -r backend/requirements.txt
   ```

   Optional: install `sentence-transformers` for higher fidelity embeddings (the system falls back to TF-IDF if the model cannot be loaded).

3. Configure the database connection (defaults to `sqlite:///./app.db`). To use PostgreSQL set the `DATABASE_URL` environment variable, e.g.:

   ```bash
   export DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/menmo
   ```

4. (Optional) Configure Supabase credentials to mirror journey data into your Supabase project:

   ```bash
   export SUPABASE_URL="https://YOUR-PROJECT.supabase.co"
   export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
   # Optionally override default table names
   # export SUPABASE_MATCH_TABLE="matches"
   # export SUPABASE_TASK_TABLE="remediation_tasks"
   ```

   The integration performs best-effort upserts after the funding match and gap-plan stages. Tables should expose JSON columns for payload fields.

5. Run the API locally (table creation is handled automatically on startup):

   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

6. (Optional) Prime the database with grant programmes by POSTing to `/grants` using the schema documented below or by adapting the payload from `backend/tests/test_api.py::_ingest_sample_grants`.

   You can also harvest live opportunities from open-data portals:

   ```bash
   python -m backend.scraper.ingest
   ```

   The command fetches climate-related datasets from Data.gov and the California Open Data portal, upserts them into the `grants` table, and writes machine-readable snapshots to `backend/data/scraped_grants.json` and `backend/data/scraped_documents.json` for the RAG engine.

### Stage endpoints at a glance

| Stage | Endpoint | Purpose |
|-------|----------|---------|
| 0/1. Awareness → Quick Scan | `POST /journey/quick-scan` | Evaluates a minimal organisation profile against hard rules and returns Yes/No/Maybe with citations. |
| 2. Funding Match | `POST /journey/funding-match` | Ingests rich project data, ranks grants (0-100), stores match explanations, and attaches retrieved knowledge chunks. |
| 3. Gap-to-Yes Planner | `POST /journey/gap-plan`, `PATCH /journey/tasks/{id}` | Converts blockers into tasks with owners/due dates, enabling Kanban-style remediation. |
| 4. Application Builder | `POST /journey/application-draft` | Generates section drafts with assumptions, citations, and compliance snapshots using the RAG utility. |
| 5. Evidence AutoCheck | `POST /journey/evidence-check` | Verifies uploaded artefacts against evidence requirements sourced from proprietary notes. |
| 6. Deadline Radar | `POST /journey/deadlines`, `GET /journey/deadlines/{user_id}` | Syncs official deadlines and internal milestones for notifications. |
| 7. Finalisation | `POST /journey/finalise` | Provides a readiness report summarising outstanding tasks and evidence gaps. |
| 8. Post Submission | `POST /journey/post-submission` | Surfaces ongoing grant updates and proprietary intelligence. |

Refer to the tests in [`backend/tests/test_api.py`](backend/tests/test_api.py) for example request payloads spanning all stages.

### Tests

Execute backend tests with:

```bash
pytest backend/tests
```

The suite provisions an in-memory SQLite database and walks through the full Menmo journey to ensure every stage remains functional.

## Frontend

The frontend lives in [`frontend/`](frontend/) and was bootstrapped with Vite + React + TypeScript. It consumes the backend APIs to provide user onboarding, grant ingestion and match browsing experiences.

### Setup

1. Install Node.js 18+.
2. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

3. Start the development server (proxies API requests to `localhost:8000`):

   ```bash
   npm run dev
   ```

4. Build production assets:

   ```bash
   npm run build
   ```

Navigate to `http://localhost:3000` to use the app. Create a user profile, ingest grants, then view recommendations on the **Recommended matches** page.

## Running the full stack locally

1. Start the backend (see instructions above).
2. In a separate terminal, start the frontend dev server.
3. The Vite proxy will forward `/api` calls to the FastAPI backend. Update `frontend/vite.config.ts` if your backend runs on a different host or port.

## Project structure

```
backend/
  db.py             # Database engine/session helpers
  main.py           # FastAPI application
  matching.py       # AI-powered grant matching service
  models.py         # SQLAlchemy ORM models
  tests/            # Pytest suites for API and matching logic
frontend/
  src/              # React source (components, pages and types)
README.md           # This file
```

## License

MIT
