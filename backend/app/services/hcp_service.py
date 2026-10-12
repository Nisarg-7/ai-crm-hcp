from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import HCP


def search_hcps(db: Session, query: str | None = None, limit: int = 50) -> list[HCP]:
    stmt = select(HCP).order_by(HCP.full_name)
    if query and query.strip():
        pattern = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                HCP.full_name.ilike(pattern),
                HCP.specialty.ilike(pattern),
                HCP.city.ilike(pattern),
                HCP.organization.ilike(pattern),
            )
        )
    return list(db.scalars(stmt.limit(limit)).all())


def get_hcp(db: Session, hcp_id: int) -> HCP | None:
    return db.get(HCP, hcp_id)