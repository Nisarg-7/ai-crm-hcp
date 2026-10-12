from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.hcp import HCPOut
from app.services import hcp_service

router = APIRouter(prefix="/hcps", tags=["hcps"])


@router.get("", response_model=list[HCPOut])
def list_hcps(
    q: str | None = Query(default=None, description="Search name, specialty, city or organization"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return hcp_service.search_hcps(db, q)


@router.get("/{hcp_id}", response_model=HCPOut)
def get_hcp(
    hcp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hcp = hcp_service.get_hcp(db, hcp_id)
    if hcp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="HCP not found"
        )
    return hcp