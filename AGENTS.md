# AI Data Analyst — Contributor Guide

## Project overview

This is a local, single-user AI data-analysis application. The frontend is React/Vite/TypeScript in `apps/web`; the backend is FastAPI/Python in `apps/api`.

The backend persists dataset metadata and conversation history using SQLAlchemy. Docker runs PostgreSQL; local development defaults to SQLite unless `DATABASE_URL` is set. Uploaded files are stored under `DATA_DIR`.

## Running the application

### Docker (recommended)

```bash
docker compose up --build
docker compose exec ollama ollama pull qwen3.5:9b
```

Open `http://localhost:5173`. The API is exposed to the web container at port `8000`.

### Local development

Prerequisites: Node.js LTS, Python 3.11+, `uv`, and Ollama with `qwen3.5:9b` pulled.

```bash
npm run setup
npm run dev
```

The web app runs on `http://localhost:5173`; FastAPI runs on `http://localhost:8000` and its OpenAPI documentation is at `/docs`.

Useful commands:

```bash
uv run --project apps/api --directory apps/api python -m pytest -q
npm run build
```

Copy `.env.example` to `.env` to override `DATABASE_URL`, `DATA_DIR`, `MAX_UPLOAD_BYTES`, or `OLLAMA_MODEL`.

## What is implemented

- CSV, XLSX, and Parquet upload with a configurable 100 MB upload limit.
- Dataset preview and automated profiling: schema, missing values, duplicates, numeric summaries, distinct counts, samples, and quality warnings.
- Persistent datasets, conversations, and message history.
- A LangGraph workflow with dedicated Analyst, Visualization, Statistics, and Report nodes.
- Safe typed analysis: no LLM-generated Python execution; DuckDB accepts only validated read-only `SELECT` SQL.
- Descriptive analysis, correlation and normality testing, Welch t-tests, robust-z-score and Isolation Forest anomaly detection.
- Automatic bar/histogram chart selection, structured analysis cards, and on-demand PDF report downloads.
- Docker Compose services for PostgreSQL, Ollama, the API, and the React client.

## Engineering rules

- Keep all calculations in trusted Python/SQL code. Never reintroduce `eval`, `exec`, or direct execution of LLM-generated code.
- Add a typed backend response and matching TypeScript contract for every analysis capability.
- Keep SQL read-only and scoped to the registered `dataset` table.
- Add unit tests for routing and calculation behavior; run backend tests and the frontend build before committing.
- Preserve database compatibility with PostgreSQL and local SQLite. Use migrations before making destructive schema changes.
- Do not commit uploads, database files, model files, tokens, or `.env` files.

## Next priorities

1. Add real database migrations (Alembic) and integration tests for API persistence and report downloads.
2. Improve natural-language intent extraction so aggregation, grouping, filters, and time-series questions map to more precise typed operations.
3. Render production chart specifications with a dedicated interactive chart library and include every chart type in PDFs.
4. Add dataset lifecycle controls: delete, retention limits, provenance, and storage cleanup.
5. Add observability, background report jobs for large datasets, authentication/multi-user isolation if the product moves beyond local use.
6. Replace the current heuristic method router with constrained LLM structured output while retaining deterministic validation and trusted execution.
