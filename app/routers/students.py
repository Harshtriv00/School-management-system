from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.result import Result
from app.models.students import Student
from app.models.classroom import Classroom
from app.schemas.results import ResultResponse
from app.schemas.student import StudentCreate, StudentOut
from app.security import get_current_user, require_role

router = APIRouter(prefix="/students", tags=["Students"])

def get_current_student_record(db: Session, current_user):
    return db.query(Student).filter(Student.email == current_user.email).first()

def format_student(student: Student):
    return {
        "id": student.id,
        "roll_no": student.roll_no,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "address": student.address,
        "father_name": student.father_name,
        "mother_name": student.mother_name,
        "classroom_id": student.classroom_id,
        "class_name": student.classroom.class_name if student.classroom else None,
        "section": student.classroom.section if student.classroom else None
    }
@router.post("/", response_model=StudentOut)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    # Check classroom exists
    classroom = db.query(Classroom).filter(Classroom.id == student.classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # Check duplicate roll_no
    existing = db.query(Student).filter(Student.roll_no == student.roll_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="Roll number already exists")

    new_student = Student(**student.model_dump())

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return format_student(new_student)

@router.get("/", response_model=list[StudentOut])
def get_students(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role == "student":
        student = get_current_student_record(db, current_user)
        return [format_student(student)] if student else []

    require_role(current_user, ["admin", "teacher"])

    students = db.query(Student).all()
    return [format_student(s) for s in students]

@router.get("/{student_id}/results", response_model=list[ResultResponse])
def get_student_results(
    student_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role == "student" and student.email != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized")

    require_role(current_user, ["admin", "teacher", "student"])

    return db.query(Result).filter(
        Result.student_roll_no == student.roll_no
    ).all()

@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role == "student" and student.email != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized")

    require_role(current_user, ["admin", "teacher", "student"])

    return format_student(student)

@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int,
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check classroom exists
    classroom = db.query(Classroom).filter(Classroom.id == student.classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # Check duplicate roll_no
    existing = db.query(Student).filter(
        Student.roll_no == student.roll_no,
        Student.id != student_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Roll number already exists")

    # Update fields
    for key, value in student.model_dump().items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)

    return format_student(db_student)

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    db_student = db.query(Student).filter(Student.id == student_id).first()

    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(db_student)
    db.commit()

    return {"message": "Student deleted successfully"} 
