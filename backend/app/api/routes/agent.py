from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agent import graph
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.agent import MAX_HISTORY_MESSAGES, ChatRequest, ChatResponse

router = APIRouter(prefix="/agent", tags=["agent"])


def trim_history(messages) -> list[tuple[str, str]]:
    recent = messages[-MAX_HISTORY_MESSAGES:]
    while recent and recent[0].role != "user":
        recent = recent[1:]
    return [(m.role, m.content) for m in recent]


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = trim_history(payload.messages)
    reply = graph.run_agent(db, current_user.id, history)
    return ChatResponse(reply=reply)