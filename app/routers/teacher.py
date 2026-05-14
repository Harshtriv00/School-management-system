from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherResponse
from app.security import get_current_user, require_role

router = APIRouter(prefix="/teachers", tags=["Teachers"])

#  CREATE TEACHER (ADMIN ONLY)
@router.post("/", response_model=TeacherResponse)
def create_teacher(
    data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    #  Check duplicate employee_id
    existing = db.query(Teacher).filter(
        Teacher.employee_id == data.employee_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists"
        )
    #  Create teacher
    teacher = Teacher(**data.model_dump())

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return teacher

#  GET ALL TEACHERS (ADMIN + TEACHER)
@router.get("/", response_model=list[TeacherResponse])
def get_teachers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin", "teacher"])

    teachers = db.query(Teacher).all()

    #  CLEAN INVALID EMAILS (prevents crash)
    for t in teachers:
        if t.email and "@" not in t.email:
            t.email = None

    return teachers

#  GET SINGLE TEACHER
@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin", "teacher"])

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    #  Fix invalid email
    if teacher.email and "@" not in teacher.email:
        teacher.email = None

    return teacher

#  UPDATE TEACHER (ADMIN ONLY)
@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    #  Update fields
    for key, value in data.model_dump().items():
        setattr(teacher, key, value)

    db.commit()
    db.refresh(teacher)

    return teacher 

#  DELETE TEACHER (ADMIN ONLY)
@router.delete("/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    db.delete(teacher)
    db.commit()

    return {"message": "Teacher deleted successfully"} 