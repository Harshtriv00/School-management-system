from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.classroom import Classroom
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
 