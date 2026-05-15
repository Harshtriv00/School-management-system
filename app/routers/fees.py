from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Literal
from app.database import get_db
from app.models.fees import Fee
from app.schemas.fees import FeeCreate, FeeResponse
from app.security import get_current_user, require_role

router = APIRouter(prefix="/fees", tags=["Fees"])

#  Admin Only
@router.post("/", response_model=FeeResponse)
def add_fee(
    data: FeeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    #  Role check
    require_role(current_user, ["admin"])

    fee = Fee(**data.model_dump())
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee

@router.get("/", response_model=list[FeeResponse])
def get_fees(
    student_id: int | None = None,
    status: Literal["pending", "paid"] | None = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin", "teacher"])

    query = db.query(Fee)

    if student_id:
        query = query.filter(Fee.student_id == student_id)

    if status:
        query = query.filter(Fee.status == status)

    return query.all()

@router.get("/{fee_id}", response_model=FeeResponse)
def get_fee(
    fee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin", "teacher"])

    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee not found")

    return fee
