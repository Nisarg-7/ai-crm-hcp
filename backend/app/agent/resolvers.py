from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import HCP, Product
from app.services import hcp_service


@dataclass
class HCPResolution:
    hcp: HCP | None = None
    message: str | None = None


def describe_hcp(hcp: HCP) -> str:
    parts = [hcp.specialty, hcp.organization, hcp.city]
    details = ", ".join(p for p in parts if p)
    return f"{hcp.full_name} ({details})" if details else hcp.full_name


def resolve_hcp(db: Session, name: str) -> HCPResolution:
    name = (name or "").strip()
    if not name:
        return HCPResolution(message="No HCP name was given. Ask the rep which HCP.")

    matches = hcp_service.search_hcps(db, name, limit=5)

    if not matches:
        # "Dr. Kapoor" may not match "Dr. Rohan Kapoor", so retry with the last word
        words = name.replace(".", " ").split()
        if len(words) > 1:
            matches = hcp_service.search_hcps(db, words[-1], limit=5)

    if not matches:
        return HCPResolution(message=f"No HCP found matching '{name}'. Ask the rep to check the name.")
    if len(matches) > 1:
        options = "; ".join(describe_hcp(h) for h in matches)
        return HCPResolution(message=f"Several HCPs match '{name}': {options}. Ask the rep which one.")
    return HCPResolution(hcp=matches[0])


def resolve_products(db: Session, names: list[str]) -> tuple[list[int], list[str]]:
    """Returns (product_ids, problems). Each name must match exactly one product."""
    ids: list[int] = []
    problems: list[str] = []
    for raw in names:
        name = raw.strip()
        if not name:
            continue
        matches = list(
            db.scalars(select(Product).where(Product.name.ilike(f"%{name}%"))).all()
        )
        if len(matches) == 1:
            ids.append(matches[0].id)
        elif not matches:
            problems.append(f"No product found matching '{name}'.")
        else:
            options = ", ".join(p.name for p in matches)
            problems.append(f"Several products match '{name}': {options}.")
    return ids, problems