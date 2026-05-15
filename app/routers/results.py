from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.result import Result
from app.models.students import Student
from app.schemas.results import ResultCreate, ResultResponse, ResultUpdate
from app.security import get_current_user, require_role

router = APIRouter(prefix="/results", tags=["Results"])

def get_current_student_record(db: Session, current_user):
    return db.query(Student).filter(Student.email == current_user.email).first()

#  Teacher Only
@router.post("/", response_model=ResultResponse)
def add_result(
    data: ResultCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    #  Role check
    require_role(current_user, ["admin"])

    student = db.query(Student).filter(
        Student.roll_no == data.student_roll_no
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found for this roll number"
        )

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

    #  Student → only results for the student linked by email
    elif current_user.role == "student":
        student = get_current_student_record(db, current_user)
        if not student:
            return []

        return db.query(Result).filter(
            Result.student_roll_no == student.roll_no
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

    if current_user.role == "student":
        student = get_current_student_record(db, current_user)
        if not student or result.student_roll_no != student.roll_no:
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

    updates = data.model_dump(exclude_unset=True)
    new_marks = updates.get("marks", result.marks)
    new_total_marks = updates.get("total_marks", result.total_marks)

    if new_marks is not None and new_total_marks is not None and new_marks > new_total_marks:
        raise HTTPException(
            status_code=400,
            detail="marks cannot be greater than total_marks"
        )

    for key, value in updates.items():
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
