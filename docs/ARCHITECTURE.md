# Architecture

## Stack
React (Vite) + Redux Toolkit | FastAPI | PostgreSQL 17 | LangGraph | Groq (openai/gpt-oss-120b)

## Layers
React UI -> Redux store -> axios -> FastAPI routes -> services -> SQLAlchemy -> PostgreSQL
                                          \-> LangGraph agent -> Groq LLM -> tools -> services

## Conventions
- Backend: routes are thin; business logic lives in services; DB access via SQLAlchemy sessions.
- AI output never goes straight to the DB: it passes through Pydantic validation first.
- Secrets only in .env (never committed). Model names come from config.
- Deterministic work (CRUD, validation, auth) is plain code. AI is used for intent, extraction, summarization, tool selection.
- Structured form and AI chat both end in the same validated save path.