from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.interaction import (
    InteractionCreate,
    InteractionOut,
    InteractionUpdate,
)
from app.services import interaction_service
from app.services.errors import ServiceError

router = APIRouter(prefix="/interactions", tags=["interactions"])


def _raise_http(err: ServiceError):
    raise HTTPException(status_code=err.status_code, detail=err.message)


@router.post("", response_model=InteractionOut, status_code=status.HTTP_201_CREATED)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return interaction_service.create_interaction(db, current_user.id, payload)
    except ServiceError as err:
        _raise_http(err)


@router.get("", response_model=list[InteractionOut])
def list_interactions(
    hcp_id: int | None = Query(default=None, description="Filter by HCP"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return interaction_service.list_interactions(db, current_user.id, hcp_id)


@router.get("/{interaction_id}", response_model=InteractionOut)
def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return interaction_service.get_interaction(db, current_user.id, interaction_id)
    except ServiceError as err:
        _raise_http(err)


@router.patch("/{interaction_id}", response_model=InteractionOut)
def update_interaction(
    interaction_id: int,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return interaction_service.update_interaction(
            db, current_user.id, interaction_id, payload
        )
    except ServiceError as err:
        _raise_http(err)