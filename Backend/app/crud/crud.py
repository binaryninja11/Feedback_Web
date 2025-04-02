from sqlalchemy.orm import Session
from app.models.dbmodel import Student
from app.schemas.schema import CreateStudent
from fastapi import HTTPException


async def create_student(db: Session, student: CreateStudent ):
    try:
        if db.query(Student).filter(Student.stdid == student.stdid).first():
            raise HTTPException(status_code=400, detail="Student already registered")

        new_student = Student(
            stdid=student.stdid,
            name=student.name,
            last_name=student.last_name,
            hashed_password=student.password,
            level=student.level,
            major=student.major,
            active=student.active
        )

        db.add(new_student)
        await db.commit()
        db.refresh(new_student)
        return new_student

    except HTTPException:  # Let 404 errors propagate correctly
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while deleting image: {e}")

async def get_student_by_stdid(db: Session, student_id: str):
    try:
        student = await db.query(Student).filter(Student.stdid == student_id).first()
        return student
    except Exception as e:
        raise Exception(f"An error occurred while deleting image: {e}")