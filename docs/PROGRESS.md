# Progress Log

## Decisions
- Auth: JWT with 2 seeded demo reps (no registration)
- DB: PostgreSQL 17, database crm_hcp, user crm_user
- LLM: Groq openai/gpt-oss-120b (fallback gpt-oss-20b); gemma2-9b-it and llama-3.3-70b are retired on Groq
- Python 3.12.10 venv in backend/venv; frontend is Vite React (JavaScript) with Redux Toolkit
- Deployment (Week 3): Vercel (frontend), Render (backend), hosted Postgres (Neon)

## Day 1 (done)
- Repo structure: backend/, frontend/, docs/, .github/
- Backend: config (pydantic-settings), SQLAlchemy engine/session, /api/health with DB check, CORS
- Frontend: Vite React, Inter font, axios client, Redux store + health slice, status page
- Docs: ARCHITECTURE.md, TOOLS.md, copilot-instructions.md
- QMS: big picture and the six-module story

## Next: Day 2
- Database models (User, HCP, Product, Interaction, FollowUp), seed data
- QMS: Deviation Management