from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.attendance import Attendance
from app.models.students import Student 
from app.schemas.attendance import AttendanceCreate, AttendanceResponse
from app.security import require_teacher, require_admin

router = APIRouter(prefix="/attendance", tags=["Attendance"])

#  MARK SINGLE ATTENDANCE

@router.post("/", response_model=AttendanceResponse)
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    user = Depends(require_teacher)  
):
    #  Check student exists
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")

    #  Prevent duplicate
    existing = db.query(Attendance).filter(
        Attendance.student_id == data.student_id,
        Attendance.date == data.date
    ).first()

    if existing:
        raise HTTPException(400, "Attendance already marked")

    record = Attendance(**data.dict())

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

#  GET ALL ATTENDANCE 

@router.get("/", response_model=list[AttendanceResponse])
def get_attendance(
    student_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    user = Depends(require_teacher)
):
    query = db.query(Attendance)

    if student_id:
        query = query.filter(Attendance.student_id == student_id)

    if from_date:
        query = query.filter(Attendance.date >= from_date)

    if to_date:
        query = query.filter(Attendance.date <= to_date)

    return query.all()

#  DELETE ATTENDANCE 

@router.delete("/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_admin)
):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not record:
        raise HTTPException(404, "Record not found")

    db.delete(record)
    db.commit()

    return {"msg": "Deleted successfully"}