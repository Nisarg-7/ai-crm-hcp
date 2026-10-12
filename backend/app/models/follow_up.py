from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.interaction import Interaction


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(primary_key=True)
    interaction_id: Mapped[int] = mapped_column(
        ForeignKey("interactions.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(Text)
    due_date: Mapped[date | None] = mapped_column(Date, default=None)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    interaction: Mapped[Interaction] = relationship(back_populates="follow_ups")