from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HCPOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    specialty: str | None = None
    organization: str | None = None
    city: str | None = None
    email: str | None = None
    phone: str | None = None
    created_at: datetime