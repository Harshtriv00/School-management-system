from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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

#  Admin + Teacher
@router.get("/")
def get_fees(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])  

    return {"message": "Fees data"}