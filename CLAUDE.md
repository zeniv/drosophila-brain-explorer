# CLAUDE.md — Project Instructions for Drosophila Brain Explorer

## Project Overview

This is a full-stack web platform for simulating neural circuits of the Drosophila melanogaster brain.
Based on Shiu et al., Nature 634, 210–218 (2024). GitHub: zeniv/drosophila-brain-explorer.

## Key Commands

```bash
# Backend (Python 3.11, venv)
cd backend && .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000

# Frontend (React 18, Vite)
cd frontend && npm run dev   # port 3000, proxy /api → localhost:8000

# Generate PDF guide
cd backend && .venv/Scripts/python.exe ../scripts/make_guide_pdf.py

# Tests
cd backend && pytest tests/ -v
```

## Architecture

- **Frontend:** React 18 + TypeScript + Vite + Tailwind + Recharts + Zustand
- **Backend:** FastAPI + SQLAlchemy async + Brian2 (or mock mode)
- **DB:** SQLite (dev, `backend/dro_dev.db`) / PostgreSQL (prod)
- **Data:** `data/connections.parquet` (15M synapses), `data/completeness.csv` (138k neurons) — NOT in git

## Critical Code Patterns

- Connectome columns are renamed on load: `Presynaptic_ID → pre_root_id`, `Unnamed: 0 → root_id`
- Brian2 is lazy-imported; when absent, mock mode activates using real connectome topology
- SQLite needs `connect_args={"check_same_thread": False}`
- Backend config reads from `backend/.env.dev` (Pydantic Settings)
- Vite proxy: `/api` → `http://localhost:8000` (or 8001 if port busy)

## User Context

- User speaks Russian; code and docs are in English
- Goal: produce arXiv publication using this simulation platform
- Yandex Cloud deployment deferred ("яндекс пока не нужен")
- Brian2 not installed locally — mock mode is active

## Full Context Recovery

Read `docs/MEMORY.md` for complete project state including:
- All file locations, tech stack, exact model parameters
- Named neuron circuits (Gr5a→MN9, JON→aDN2)
- Known issues and fixes
- Pending work items
- Git history
