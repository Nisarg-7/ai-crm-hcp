from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.hcp import HCPOut
from app.schemas.product import ProductOut

InteractionType = Literal["visit", "call", "email", "conference"]
Sentiment = Literal["positive", "neutral", "negative"]
Source = Literal["form", "ai_chat"]
FollowUpStatus = Literal["pending", "done", "cancelled"]


class FollowUpCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1, max_length=500)
    due_date: date | None = None


class FollowUpOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    due_date: date | None = None
    status: FollowUpStatus
    created_at: datetime


class InteractionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hcp_id: int
    interaction_type: InteractionType
    interaction_date: datetime
    sentiment: Sentiment | None = None
    summary: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=5000)
    source: Source = "form"
    product_ids: list[int] = Field(default_factory=list)
    follow_ups: list[FollowUpCreate] = Field(default_factory=list)


class InteractionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interaction_type: InteractionType | None = None
    interaction_date: datetime | None = None
    sentiment: Sentiment | None = None
    summary: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=5000)
    product_ids: list[int] | None = None


class InteractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rep_id: int
    hcp_id: int
    hcp: HCPOut
    interaction_type: str
    interaction_date: datetime
    sentiment: str | None = None
    summary: str | None = None
    notes: str | None = None
    source: str
    products: list[ProductOut] = []
    follow_ups: list[FollowUpOut] = []
    created_at: datetime
    updated_at: datetime