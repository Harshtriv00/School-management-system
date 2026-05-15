from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.result import Result
from app.schemas.results import ResultCreate, ResultResponse, ResultUpdate
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

    #  Student → only matching roll number if username is roll number
    elif current_user.role == "student":
        return db.query(Result).filter(
            Result.student_roll_no == current_user.username
        ).all()

    #  Other roles not allowed
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/{result_id}", response_model=ResultResponse)
def get_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    if current_user.role == "student" and result.student_roll_no != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized")

    require_role(current_user, ["admin", "teacher", "student"])
    return result

@router.put("/{result_id}", response_model=ResultResponse)
def update_result(
    result_id: int,
    data: ResultUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin", "teacher"])

    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(result, key, value)

    db.commit()
    db.refresh(result)

    return result

@router.delete("/{result_id}")
def delete_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    db.delete(result)
    db.commit()

    return {"message": "Result deleted successfully"}
