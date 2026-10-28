import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, auth, dashboard, health, hcps, interactions, products 
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI-First CRM: HCP Module", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(hcps.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")