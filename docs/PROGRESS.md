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

## Day 6 (done)
- Backend: GET /api/products (protected)
- Redux: productsSlice; interactionsSlice extended with createInteraction (422 error mapping, resetCreate)
- Components: LogInteractionForm (HCP picker, type, date, sentiment, products, summary, notes, dynamic follow-ups)
- Page: LogInteractionPage with tabs (Structured Form active, AI Conversation placeholder), route and nav link
- Form state is local (useState); Redux is used on submit only
- QMS: Adverse Event Reporting (docs/qms/06-adverse-events.md)

## Day 7 (done)
- Redux: interactionsSlice extended with fetchInteractionById, updateInteraction, resetUpdate; shared mapError helper
- Pages: EditInteractionPage (HCP and follow-ups read-only, PATCH sends editable fields), MyInteractionsPage
- Routing: /interactions and /interactions/:id/edit; Edit links on history cards; nav link
- Backend tests (pytest): separate crm_hcp_test database with a safety guard, fixtures (make_user, make_hcp, make_product, auth_headers), 28 tests for health, auth, HCPs and interactions
- QMS: Recall Management (docs/qms/07-recall.md). All six core modules covered.

## Next: Day 8 (Week 2 begins)
- LangGraph and Groq: first working agent, tool-calling test against openai/gpt-oss-120b
- Finalize the tool list and agent architecture (docs/TOOLS.md)
- QMS: how the modules connect (08) and the qms README index