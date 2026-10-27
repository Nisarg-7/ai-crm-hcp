from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_HISTORY_MESSAGES = 10


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be blank")
        return value


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: list[ChatMessage] = Field(min_length=1, max_length=50)

    @field_validator("messages")
    @classmethod
    def last_is_user(cls, value: list[ChatMessage]) -> list[ChatMessage]:
        if value[-1].role != "user":
            raise ValueError("The last message must be from the user")
        return value


class InteractionCard(BaseModel):
    action: Literal["logged", "edited", "follow_up_added"]
    interaction_id: int
    hcp_id: int
    hcp_name: str
    interaction_type: str
    interaction_date: str
    sentiment: str | None = None
    products: list[str] = []
    follow_ups: list[str] = []


class ChatResponse(BaseModel):
    reply: str
    actions: list[InteractionCard] = []