import logging
from datetime import date, datetime
from typing import Literal

from langchain_core.tools import tool
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.agent.resolvers import describe_hcp, resolve_hcp, resolve_products
from app.schemas.interaction import FollowUpCreate, InteractionCreate, InteractionUpdate
from app.services import hcp_service, interaction_service
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)

def format_interaction(i) -> str:
    products = ", ".join(p.name for p in i.products) or "none"
    follow_ups = "; ".join(
        f"{f.description} (due {f.due_date or 'no date'}, {f.status})" for f in i.follow_ups
    ) or "none"
    return (
        f"#{i.id} | {i.interaction_date:%Y-%m-%d} | {i.interaction_type} | "
        f"sentiment: {i.sentiment or 'not set'} | products: {products} | "
        f"summary: {i.summary or 'none'} | follow-ups: {follow_ups}"
    )

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

    @tool
    def get_interaction_history(hcp_name: str, limit: int = 5) -> str:
        """Show the rep's most recent interactions with one HCP, newest first.
        Use this when the rep asks about past meetings, calls or emails with an HCP.
        limit is how many to show (1 to 10)."""
        resolution = resolve_hcp(db, hcp_name)
        if resolution.hcp is None:
            return resolution.message or "Could not identify the HCP."
        hcp = resolution.hcp

        limit = max(1, min(limit, 10))
        try:
            rows = interaction_service.list_interactions(db, rep_id, hcp.id, limit=limit)
        except Exception:
            logger.exception("get_interaction_history failed")
            db.rollback()
            return "Could not load the history. Tell the rep to try again."

        if not rows:
            return f"No interactions logged with {hcp.full_name} yet."
        lines = [format_interaction(r) for r in rows]
        return f"Last {len(rows)} interaction(s) with {hcp.full_name}:\n" + "\n".join(lines)

    @tool
    def edit_interaction(
        hcp_name: str,
        interaction_id: int | None = None,
        interaction_type: Literal["visit", "call", "email", "conference"] | None = None,
        interaction_date: str | None = None,
        sentiment: Literal["positive", "neutral", "negative"] | None = None,
        summary: str | None = None,
        notes: str | None = None,
        product_names: list[str] | None = None,
    ) -> str:
        """Change fields of an existing interaction. Only pass the fields the rep
        wants to change. If interaction_id is not given, the most recent interaction
        with that HCP is edited. interaction_date is an ISO 8601 timestamp.
        Cannot change the HCP and cannot delete anything."""
        resolution = resolve_hcp(db, hcp_name)
        if resolution.hcp is None:
            return resolution.message or "Could not identify the HCP."
        hcp = resolution.hcp

        changes: dict = {}
        if interaction_type is not None:
            changes["interaction_type"] = interaction_type
        if sentiment is not None:
            changes["sentiment"] = sentiment
        if summary is not None:
            changes["summary"] = summary
        if notes is not None:
            changes["notes"] = notes
        if interaction_date:
            try:
                changes["interaction_date"] = datetime.fromisoformat(
                    interaction_date.replace("Z", "+00:00")
                )
            except ValueError:
                return "Not changed. The date must be ISO 8601, e.g. 2026-10-21T10:00:00Z."
        if product_names is not None:
            product_ids, problems = resolve_products(db, product_names)
            if problems:
                return "Not changed. " + " ".join(problems) + " Ask the rep to clarify."
            changes["product_ids"] = product_ids

        if not changes:
            return "Nothing to change. Ask the rep which field to update."

        try:
            if interaction_id is None:
                rows = interaction_service.list_interactions(db, rep_id, hcp.id, limit=1)
                if not rows:
                    return f"No interactions logged with {hcp.full_name} to edit."
                interaction_id = rows[0].id
            else:
                target = interaction_service.get_interaction(db, rep_id, interaction_id)
                if target.hcp_id != hcp.id:
                    return f"Interaction #{interaction_id} is not with {hcp.full_name}. Ask the rep to confirm."

            update = InteractionUpdate(**changes)
            saved = interaction_service.update_interaction(db, rep_id, interaction_id, update)
        except ValidationError as err:
            db.rollback()
            return f"Not changed. Invalid details: {err}. Ask the rep to correct them."
        except ServiceError as err:
            db.rollback()
            return f"Not changed. {err.message}"
        except Exception:
            logger.exception("edit_interaction failed")
            db.rollback()
            return "Not changed. Something went wrong on our side. Tell the rep to try again."

        return "Updated interaction:\n" + format_interaction(saved)


    @tool
    def schedule_followup(
        hcp_name: str,
        description: str,
        due_date: str | None = None,
        interaction_id: int | None = None,
    ) -> str:
        """Add a follow-up action to an existing interaction with an HCP.
        due_date is YYYY-MM-DD. If interaction_id is not given, the follow-up is
        attached to the most recent interaction with that HCP.
        Use this for reminders such as 'send the PDF by Friday'."""
        resolution = resolve_hcp(db, hcp_name)
        if resolution.hcp is None:
            return resolution.message or "Could not identify the HCP."
        hcp = resolution.hcp

        try:
            due = date.fromisoformat(due_date) if due_date else None
        except ValueError:
            return "Not saved. The due date must be YYYY-MM-DD."

        try:
            data = FollowUpCreate(description=description, due_date=due)
        except ValidationError as err:
            return f"Not saved. Invalid details: {err}. Ask the rep to correct them."

        try:
            if interaction_id is None:
                rows = interaction_service.list_interactions(db, rep_id, hcp.id, limit=1)
                if not rows:
                    return f"No interactions logged with {hcp.full_name} to attach a follow-up to."
                interaction_id = rows[0].id
            else:
                target = interaction_service.get_interaction(db, rep_id, interaction_id)
                if target.hcp_id != hcp.id:
                    return f"Interaction #{interaction_id} is not with {hcp.full_name}. Ask the rep to confirm."

            saved = interaction_service.add_follow_up(db, rep_id, interaction_id, data)
        except ServiceError as err:
            db.rollback()
            return f"Not saved. {err.message}"
        except Exception:
            logger.exception("schedule_followup failed")
            db.rollback()
            return "Not saved. Something went wrong on our side. Tell the rep to try again."

        return (
            f"Follow-up added to interaction #{saved.id} with {hcp.full_name} "
            f"({saved.interaction_date:%Y-%m-%d}): {data.description}, due {due or 'no date'}."
        )

    return [search_hcp, log_interaction, get_interaction_history, edit_interaction, schedule_followup]