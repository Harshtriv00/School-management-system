from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.result import Result
from app.schemas.results import ResultCreate, ResultResponse
from app.security import get_current_user, require_role

router = APIRouter(prefix="/results", tags=["Results"])

#  Teacher Only
@router.post("/", response_model=ResultResponse)
def add_result(
    data: ResultCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    #  Role check
    require_role(current_user, ["admin"])

    result = Result(**data.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

@router.get("/", response_model=list[ResultResponse])
def get_results(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    #  Admin → all results
    if current_user.role == "admin":
        return db.query(Result).all()

    #  Teacher → all results (you can later filter by class)
    elif current_user.role == "teacher":
        return db.query(Result).all()

    #  Student → only their result
    elif current_user.role == "student":
        return db.query(Result).filter(
            Result.student_id == current_user.id
        ).all()

    #  Other roles not allowed
    else:
        raise HTTPException(status_code=403, detail="Not authorized")