from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import HCP


def _run_search(db: Session, pattern: str, limit: int) -> list[HCP]:
    stmt = (
        select(HCP)
        .where(
            or_(
                HCP.full_name.ilike(pattern),
                HCP.specialty.ilike(pattern),
                HCP.city.ilike(pattern),
                HCP.organization.ilike(pattern),
            )
        )
        .order_by(HCP.full_name)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def search_hcps(db: Session, query: str | None = None, limit: int = 50) -> list[HCP]:
    if not query or not query.strip():
        stmt = select(HCP).order_by(HCP.full_name).limit(limit)
        return list(db.scalars(stmt).all())

    query = query.strip()
    results = _run_search(db, f"%{query}%", limit)
    if results:
        return results

    # Fallback: "cardiologists" should still find "Cardiology".
    # Retry with each word shortened to its first 5 letters.
    words = [w for w in query.replace(",", " ").split() if len(w) > 5]
    for word in words:
        results = _run_search(db, f"%{word[:5]}%", limit)
        if results:
            return results
    return []


def get_hcp(db: Session, hcp_id: int) -> HCP | None:
    return db.get(HCP, hcp_id)