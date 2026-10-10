# Copilot instructions

This is a full-stack portfolio project: React + Redux Toolkit frontend, FastAPI + SQLAlchemy backend, PostgreSQL, LangGraph agent with Groq.
Read docs/ARCHITECTURE.md and docs/TOOLS.md before suggesting structural changes.

Rules:
- Backend: Python 3.12, type hints, Pydantic v2 schemas, thin routes, logic in services.
- Frontend: functional React components, Redux Toolkit slices, axios client from src/api/client.js.
- Never hard-code secrets; read config from environment.
- Keep code simple and readable. Do not add libraries without asking.