from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import HCP, FollowUp, Interaction, Product
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from app.services.errors import ServiceError


def _load_products(db: Session, product_ids: list[int]) -> list[Product]:
    unique_ids = list(dict.fromkeys(product_ids))
    if not unique_ids:
        return []
    products = list(db.scalars(select(Product).where(Product.id.in_(unique_ids))).all())
    if len(products) != len(unique_ids):
        raise ServiceError("One or more products do not exist", 400)
    return products


def _with_relations(stmt):
    return stmt.options(
        selectinload(Interaction.hcp),
        selectinload(Interaction.products),
        selectinload(Interaction.follow_ups),
    )


def create_interaction(db: Session, rep_id: int, data: InteractionCreate) -> Interaction:
    if db.get(HCP, data.hcp_id) is None:
        raise ServiceError("HCP not found", 404)

    interaction = Interaction(
        rep_id=rep_id,
        hcp_id=data.hcp_id,
        interaction_type=data.interaction_type,
        interaction_date=data.interaction_date,
        sentiment=data.sentiment,
        summary=data.summary,
        notes=data.notes,
        source=data.source,
        products=_load_products(db, data.product_ids),
        follow_ups=[
            FollowUp(description=f.description, due_date=f.due_date)
            for f in data.follow_ups
        ],
    )
    db.add(interaction)
    db.commit()
    return get_interaction(db, rep_id, interaction.id)


def list_interactions(
    db: Session, rep_id: int, hcp_id: int | None = None, limit: int = 50
) -> list[Interaction]:
    stmt = select(Interaction).where(Interaction.rep_id == rep_id)
    if hcp_id is not None:
        stmt = stmt.where(Interaction.hcp_id == hcp_id)
    stmt = _with_relations(stmt).order_by(Interaction.interaction_date.desc()).limit(limit)
    return list(db.scalars(stmt).all())


def get_interaction(db: Session, rep_id: int, interaction_id: int) -> Interaction:
    stmt = _with_relations(
        select(Interaction).where(
            Interaction.id == interaction_id, Interaction.rep_id == rep_id
        )
    )
    interaction = db.scalars(stmt).first()
    if interaction is None:
        raise ServiceError("Interaction not found", 404)
    return interaction


def update_interaction(
    db: Session, rep_id: int, interaction_id: int, data: InteractionUpdate
) -> Interaction:
    interaction = get_interaction(db, rep_id, interaction_id)
    changes = data.model_dump(exclude_unset=True)

    if "product_ids" in changes:
        product_ids = changes.pop("product_ids")
        if product_ids is not None:
            interaction.products = _load_products(db, product_ids)

    for field, value in changes.items():
        if field in ("interaction_type", "interaction_date") and value is None:
            continue  # these columns are required, so ignore an explicit null
        setattr(interaction, field, value)

    db.commit()
    return get_interaction(db, rep_id, interaction_id)