import logging
from datetime import date, datetime
from typing import Literal

from langchain_core.tools import tool
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.agent.resolvers import describe_hcp, resolve_hcp, resolve_products
from app.schemas.interaction import FollowUpCreate, InteractionCreate
from app.services import hcp_service, interaction_service
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)


def build_tools(db: Session, rep_id: int) -> list:
    @tool
    def search_hcp(query: str) -> str:
        """Find Healthcare Professionals by name, specialty, city or hospital.
        Use a short query such as 'Kapoor', 'cardiology' or 'Navi Mumbai'.
        Search once per request and trust the result."""
        try:
            matches = hcp_service.search_hcps(db, query, limit=10)
        except Exception:
            logger.exception("search_hcp failed")
            db.rollback()
            return "The HCP search failed. Tell the rep to try again."

        if not matches:
            return f"No HCPs found for '{query}'."
        lines = [f"- {describe_hcp(h)}" for h in matches]
        return f"Found {len(matches)} HCP(s):\n" + "\n".join(lines)

    @tool
    def log_interaction(
        hcp_name: str,
        interaction_type: Literal["visit", "call", "email", "conference"],
        interaction_date: str | None = None,
        sentiment: Literal["positive", "neutral", "negative"] | None = None,
        summary: str | None = None,
        notes: str | None = None,
        product_names: list[str] | None = None,
        follow_up_description: str | None = None,
        follow_up_due_date: str | None = None,
    ) -> str:
        """Save a new interaction between the rep and an HCP.
        Only call this when the HCP and the interaction type are clear.
        interaction_date is an ISO 8601 timestamp such as 2026-10-21T10:00:00Z;
        leave it empty for 'now'. follow_up_due_date is YYYY-MM-DD.
        Only set sentiment if the rep expressed it. Never invent details."""
        resolution = resolve_hcp(db, hcp_name)
        if resolution.hcp is None:
            return resolution.message or "Could not identify the HCP."
        hcp = resolution.hcp

        product_ids, problems = resolve_products(db, product_names or [])
        if problems:
            return "Not saved. " + " ".join(problems) + " Ask the rep to clarify."

        follow_ups = []
        if follow_up_description:
            try:
                due = date.fromisoformat(follow_up_due_date) if follow_up_due_date else None
            except ValueError:
                return "Not saved. The follow-up due date must be YYYY-MM-DD."
            follow_ups.append(FollowUpCreate(description=follow_up_description, due_date=due))

        try:
            when = (
                datetime.fromisoformat(interaction_date.replace("Z", "+00:00"))
                if interaction_date
                else datetime.now().astimezone()
            )
            data = InteractionCreate(
                hcp_id=hcp.id,
                interaction_type=interaction_type,
                interaction_date=when,
                sentiment=sentiment,
                summary=summary,
                notes=notes,
                source="ai_chat",
                product_ids=product_ids,
                follow_ups=follow_ups,
            )
        except (ValidationError, ValueError) as err:
            return f"Not saved. Invalid details: {err}. Ask the rep to correct them."

        try:
            saved = interaction_service.create_interaction(db, rep_id, data)
        except ServiceError as err:
            db.rollback()
            return f"Not saved. {err.message}"
        except Exception:
            logger.exception("log_interaction failed")
            db.rollback()
            return "Not saved. Something went wrong on our side. Tell the rep to try again."

        products = ", ".join(p.name for p in saved.products) or "none"
        return (
            f"Saved interaction #{saved.id}: {saved.interaction_type} with "
            f"{hcp.full_name} on {saved.interaction_date:%Y-%m-%d}. "
            f"Sentiment: {saved.sentiment or 'not set'}. Products: {products}. "
            f"Follow-ups: {len(saved.follow_ups)}."
        )

    return [search_hcp, log_interaction]