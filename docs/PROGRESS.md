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

## Day 8 (done)
- Installed langgraph and langchain-groq; Groq key verified
- Scratch tests (git-ignored): direct Groq call, tool-calling test, minimal LangGraph agent (agent node, tool node, tools_condition loop)
- Findings: gpt-oss-120b picks tools reliably, handles two-step requests, asks when details are missing; invented "meeting" as a type until Literal typing was used; repeated searches with a dummy tool (fix: system prompt and step limit)
- Design point: tools must resolve HCP names to ids and return clarifying text on zero or multiple matches
- docs/TOOLS.md finalized (5 tools plus optional suggest_next_action)
- QMS: how modules connect (08) and docs/qms/README.md index. QMS series complete.

## Day 9 (done)
- backend/app/agent package: prompts.py (system prompt with current date), resolvers.py (HCP and product name to database row), tools.py (build_tools), graph.py (build_agent, run_agent)
- Tools built so far: search_hcp, log_interaction. Both use the existing services; rep_id and db come from a closure, so the LLM cannot choose a rep
- log_interaction safety chain: resolve HCP, resolve products, validate with InteractionCreate, save via create_interaction with source "ai_chat"; failures return text to the LLM
- Graph: system prompt on every call, recursion limit of 12, fallback to gpt-oss-20b, friendly error if everything fails
- hcp_service.search_hcps: fallback to 5-letter word stems so "cardiologists" finds "Cardiology"
- Prompt rule for "this Friday" vs "next Friday"
- Tests: 43 passing (resolvers, both tools, run_agent failure and fallback, using no real LLM calls)
- Note: scratch_run.py saved a few real AI-chat interactions for rep 1 in crm_hcp (harmless demo data)

## Day 10 (done)
- interaction_service.add_follow_up (with a duplicate guard that raises a 409 ServiceError)
- Tools added in agent/tools.py: get_interaction_history, edit_interaction, schedule_followup. All five required tools now exist: log_interaction, edit_interaction, search_hcp, get_interaction_history, schedule_followup
- edit and follow-up tools take an HCP name and an optional interaction id; without an id they use that HCP's most recent interaction and report which one
- Edits go through InteractionUpdate (cannot change the HCP, cannot delete); no delete tool by design
- System prompt extended: edit and follow-up rules, history-first for older interactions, no deleting
- Real-agent run verified all five tools in a multi-turn chat; a Groq 429 (8000 tokens per minute on the free tier) was handled by the fallback model
- Finding: each request sends system prompt, tool descriptions and the whole history, so the chat screen must cap the history sent (about the last 10 messages)
- Tests: all passing (history, edit, ownership, follow-up, duplicate guard, bad dates)

## Day 11 (done)
- schemas/agent.py: ChatMessage (roles limited to user and assistant, no blank content, max 4000 chars), ChatRequest (last message must be from the user, max 50 messages, extra fields forbidden), ChatResponse
- api/routes/agent.py: POST /api/agent/chat, JWT-protected; trims history to the last 10 messages and drops leading assistant messages; rep id comes only from the token
- Route calls graph.run_agent through the module so tests can swap in a fake agent
- Verified in Swagger: search, multi-turn memory, 422 on system role, last message from assistant, blank message, and no login
- Tests: chat route tests (auth, rep id, trimming, validation, unknown field, LLM failure gives friendly reply), all passing
- Note: a transient OSError on .env during pytest was fixed by opening a fresh terminal

## Day 12 (done)
- Redux: chatSlice (messages, status, error; sendMessage, retryLast, clearChat), registered in the store
- Components: ChatPanel (message bubbles, typing indicator, example chips, Enter to send, error box with Retry, New chat)
- LogInteractionPage: AI Conversation tab (default) and Structured Form tab; both stay mounted and the inactive one is hidden, so the conversation survives tab switches
- Chat sends the full conversation each time; the backend trims it to the last 10 messages
- Verified end to end: search, log by chat, edit by chat, missing details, retry after a server error

## Next: Day 13
- Show what the agent saved as a structured card in the chat
- Refresh HCP and interaction data after the agent changes something
- Chat polish: rate-limit message, long replies