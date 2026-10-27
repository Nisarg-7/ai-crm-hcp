import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agent import graph
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.agent import (
    MAX_HISTORY_MESSAGES,
    ChatRequest,
    ChatResponse,
    InteractionCard,
)
from app.services import interaction_service
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["agent"])


def trim_history(messages) -> list[tuple[str, str]]:
    recent = messages[-MAX_HISTORY_MESSAGES:]
    while recent and recent[0].role != "user":
        recent = recent[1:]
    return [(m.role, m.content) for m in recent]


def build_cards(db: Session, rep_id: int, events: list[dict]) -> list[InteractionCard]:
    cards: list[InteractionCard] = []
    seen: set[int] = set()
    # newest event per interaction wins, so one card per interaction
    for event in reversed(events):
        interaction_id = event["interaction_id"]
        if interaction_id in seen:
            continue
        seen.add(interaction_id)
        try:
            i = interaction_service.get_interaction(db, rep_id, interaction_id)
        except ServiceError:
            continue
        cards.append(
            InteractionCard(
                action=event["type"],
                interaction_id=i.id,
                hcp_id=i.hcp_id,
                hcp_name=i.hcp.full_name,
                interaction_type=i.interaction_type,
                interaction_date=i.interaction_date.isoformat(),
                sentiment=i.sentiment,
                products=[p.name for p in i.products],
                follow_ups=[
                    f"{f.description} (due {f.due_date})" if f.due_date else f.description
                    for f in i.follow_ups
                ],
            )
        )
    cards.reverse()
    return cards


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = trim_history(payload.messages)
    reply, events = graph.run_agent(db, current_user.id, history)
    cards = build_cards(db, current_user.id, events)
    return ChatResponse(reply=reply, actions=cards)