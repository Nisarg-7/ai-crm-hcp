from datetime import date, datetime

from pydantic import BaseModel


class DashboardCounts(BaseModel):
    total_interactions: int
    last_7_days: int
    open_follow_ups: int


class RecentInteraction(BaseModel):
    id: int
    hcp_id: int
    hcp_name: str
    interaction_type: str
    interaction_date: datetime
    sentiment: str | None = None
    source: str


class OpenFollowUp(BaseModel):
    id: int
    interaction_id: int
    hcp_id: int
    hcp_name: str
    description: str
    due_date: date | None = None


class DashboardOut(BaseModel):
    counts: DashboardCounts
    recent_interactions: list[RecentInteraction]
    open_follow_ups: list[OpenFollowUp]