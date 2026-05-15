from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.attendance import Attendance
from app.models.students import Student 
from app.schemas.attendance import AttendanceBulkCreate, AttendanceCreate, AttendanceResponse
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

    record = Attendance(**data.model_dump())

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

@router.post("/bulk", response_model=list[AttendanceResponse])
def mark_bulk_attendance(
    data: AttendanceBulkCreate,
    db: Session = Depends(get_db),
    user = Depends(require_teacher)
):
    if not data.records:
        raise HTTPException(status_code=400, detail="No attendance records provided")

    seen = set()
    records = []

    for item in data.records:
        key = (item.student_id, item.date)
        if key in seen:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate attendance in request for student {item.student_id} on {item.date}"
            )
        seen.add(key)

        student = db.query(Student).filter(Student.id == item.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {item.student_id} not found")

        existing = db.query(Attendance).filter(
            Attendance.student_id == item.student_id,
            Attendance.date == item.date
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Attendance already marked for student {item.student_id} on {item.date}"
            )

        records.append(Attendance(**item.model_dump()))

    db.add_all(records)
    db.commit()

    for record in records:
        db.refresh(record)

    return records

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
