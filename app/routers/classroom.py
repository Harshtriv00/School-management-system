from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.classroom import Classroom
from app.models.students import Student
from app.schemas.classroom import ClassroomCreate, ClassroomResponse
from app.security import get_current_user, require_role

router = APIRouter(prefix="/classrooms", tags=["Classrooms"])

@router.post("/", response_model=ClassroomResponse)
def create_classroom(
    classroom: ClassroomCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    room = Classroom(**classroom.model_dump())

    db.add(room)
    db.commit()
    db.refresh(room)

    return {
        "id": room.id,
        "class_name": room.class_name,
        "section": room.section,
        "total_students": 0,      
        "students": []            
    }

@router.get("/", response_model=list[ClassroomResponse])
def get_classrooms(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin", "teacher"]) 

    classrooms = db.query(Classroom).all()

    return [
        {
            "id": room.id,
            "class_name": room.class_name,
            "section": room.section,
            "total_students": len(room.students),
            "students": room.students
        }
        for room in classrooms
    ] 

@router.get("/{classroom_id}", response_model=ClassroomResponse)
def get_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin", "teacher"])

    room = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    return {
        "id": room.id,
        "class_name": room.class_name,
        "section": room.section,
        "total_students": len(room.students),
        "students": room.students
    }

@router.put("/{classroom_id}", response_model=ClassroomResponse)
def update_classroom(
    classroom_id: int,
    classroom: ClassroomCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    room = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    room.class_name = classroom.class_name
    room.section = classroom.section

    db.commit()
    db.refresh(room)

    return {
        "id": room.id,
        "class_name": room.class_name,
        "section": room.section,
        "total_students": len(room.students),
        "students": room.students
    }

@router.delete("/{classroom_id}")
def delete_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_role(current_user, ["admin"])

    room = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    student_count = db.query(Student).filter(Student.classroom_id == classroom_id).count()
    if student_count:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete classroom with assigned students"
        )

    db.delete(room)
    db.commit()

    return {"message": "Classroom deleted successfully"}
 
