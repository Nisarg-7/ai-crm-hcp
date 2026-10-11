from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.hcp import HCP
from app.models.product import Product
from app.models.user import User

interaction_products = Table(
    "interaction_products",
    Base.metadata,
    Column(
        "interaction_id",
        ForeignKey("interactions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "product_id",
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    rep_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    hcp_id: Mapped[int] = mapped_column(ForeignKey("hcps.id"), index=True)
    interaction_type: Mapped[str] = mapped_column(String(30))
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sentiment: Mapped[str | None] = mapped_column(String(20), default=None)
    summary: Mapped[str | None] = mapped_column(Text, default=None)
    notes: Mapped[str | None] = mapped_column(Text, default=None)
    source: Mapped[str] = mapped_column(String(20), default="form")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    rep: Mapped[User] = relationship()
    hcp: Mapped[HCP] = relationship()
    products: Mapped[list[Product]] = relationship(secondary=interaction_products)