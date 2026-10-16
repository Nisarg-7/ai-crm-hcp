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

## Day 2 (done)
- Models: User, HCP, Product, Interaction, interaction_products (link table), FollowUp
- Tables created with create_tables.py (create_all); verified in pgAdmin
- core/security.py: bcrypt hash_password and verify_password
- seed.py (re-runnable): 2 reps, 10 HCPs, 5 products, 6 interactions, 5 follow-ups
- Demo logins: rep1@democrm.com and rep2@democrm.com, password Demo@1234
- QMS: Deviation Management (docs/qms/02-deviation.md)

## Day 3 (done)
- core/security.py: JWT create and decode (PyJWT), settings for algorithm and expiry
- Auth: POST /api/auth/login, GET /api/auth/me, get_current_user dependency (HTTPBearer)
- Schemas: auth, hcp, product, interaction (Literal-validated types, extra=forbid)
- Services: hcp_service (search), interaction_service (create, list, get, update), ServiceError
- Routes: /api/hcps (list, search, detail), /api/interactions (POST, GET, GET by id, PATCH)
- Rule: reps only see and edit their own interactions
- Model change: Interaction.follow_ups relationship (back_populates)
- QMS: CAPA (docs/qms/03-capa.md)

## Day 4 (done)
- Frontend: axios interceptor attaches JWT from localStorage
- Redux: authSlice (login, fetchMe, logout), registered in the store
- Pages: LoginPage (loading and error states), HomePage
- Components: ProtectedRoute (redirects, restores session on refresh), Layout (top bar, logout)
- Routing: React Router in App.jsx, BrowserRouter in main.jsx
- First run of backend and frontend together; login flow verified end to end
- QMS: Supplier Management (docs/qms/04-supplier-management.md)

## Day 5 (done)
- Redux: hcpsSlice (list and selected HCP), interactionsSlice (history per HCP)
- hooks/useDebounce (300 ms search debounce)
- Pages: HcpListPage (search, loading, error and empty states), HcpDetailPage (info plus interaction history, follow-ups, badges)
- Routing: /hcps and /hcps/:id inside the protected layout; NavLink navigation bar
- QMS: Product Complaints (docs/qms/05-product-complaints.md)

## Next: Day 6
- Log Interaction screen: structured form (HCP picker, type, date, sentiment, products, follow-ups)
- products endpoint and Redux slice
- QMS: Adverse Event Reporting