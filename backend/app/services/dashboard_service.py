from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import FollowUp, Interaction
from app.schemas.dashboard import (
    DashboardCounts,
    DashboardOut,
    OpenFollowUp,
    RecentInteraction,
)


def get_dashboard(db: Session, rep_id: int) -> DashboardOut:
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    total = db.scalar(
        select(func.count()).select_from(Interaction).where(Interaction.rep_id == rep_id)
    ) or 0
    recent_count = db.scalar(
        select(func.count())
        .select_from(Interaction)
        .where(Interaction.rep_id == rep_id, Interaction.interaction_date >= week_ago)
    ) or 0
    open_count = db.scalar(
        select(func.count())
        .select_from(FollowUp)
        .join(Interaction, FollowUp.interaction_id == Interaction.id)
        .where(Interaction.rep_id == rep_id, FollowUp.status == "pending")
    ) or 0

    recent_rows = db.scalars(
        select(Interaction)
        .where(Interaction.rep_id == rep_id)
        .options(selectinload(Interaction.hcp))
        .order_by(Interaction.interaction_date.desc())
        .limit(5)
    ).all()

    follow_rows = db.scalars(
        select(FollowUp)
        .join(Interaction, FollowUp.interaction_id == Interaction.id)
        .where(Interaction.rep_id == rep_id, FollowUp.status == "pending")
        .options(selectinload(FollowUp.interaction).selectinload(Interaction.hcp))
        .order_by(FollowUp.due_date.asc().nulls_last(), FollowUp.id)
        .limit(5)
    ).all()

    return DashboardOut(
        counts=DashboardCounts(
            total_interactions=total,
            last_7_days=recent_count,
            open_follow_ups=open_count,
        ),
        recent_interactions=[
            RecentInteraction(
                id=i.id,
                hcp_id=i.hcp_id,
                hcp_name=i.hcp.full_name,
                interaction_type=i.interaction_type,
                interaction_date=i.interaction_date,
                sentiment=i.sentiment,
                source=i.source,
            )
            for i in recent_rows
        ],
        open_follow_ups=[
            OpenFollowUp(
                id=f.id,
                interaction_id=f.interaction_id,
                hcp_id=f.interaction.hcp_id,
                hcp_name=f.interaction.hcp.full_name,
                description=f.description,
                due_date=f.due_date,
            )
            for f in follow_rows
        ],
    )