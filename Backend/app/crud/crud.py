from typing import List

from sqlalchemy.orm import Session
from app.models.dbmodel import Student, Teacher, Subject, Enrollment
from app.schemas import schema
from fastapi import HTTPException


async def create_student(db: Session, student: schema.SignUpStudent):
    if db.query(Student).filter(Student.stdid == student.stdid).first():
        raise HTTPException(status_code=400, detail="Student already registered")

    new_student = Student(
        stdid=student.stdid,
        name=student.name,
        last_name=student.last_name,
        hashed_password=student.password,
        level=student.level,
        major=student.major,
        is_active=True
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

async def get_student_by_stdid(db: Session, stdid: str):
    return db.query(Student).filter(Student.stdid == stdid).first()

async def get_student_by_id(db: Session, student_id: int):
    return db.query(Student).filter(Student.id == student_id).first()

async def get_student_by_level_and_major(db: Session, level: int, major: str) -> List[int]:
    return [student.id for student in db.query(Student).filter(Student.level == level, Student.major == major).all()]


async def create_teacher(db: Session, teacher: schema.SignUpTeacher):
    if db.query(Teacher).filter(Teacher.tid == teacher.tid).first():
        raise HTTPException(status_code=400, detail="Teacher already registered")

    new_teacher = Teacher(
        tid=teacher.tid,
        name=teacher.name,
        last_name=teacher.last_name,
        hashed_password=teacher.password,
        is_active=True
    )

    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher

async def get_teacher_by_tid(db: Session, teacher_tid: str):
    return db.query(Teacher).filter(Teacher.tid == teacher_tid).first()

async def get_teacher_by_id(db: Session, teacher_id: int):
    return db.query(Teacher).filter(Teacher.id == teacher_id).first()


async def get_subject_by_id(db: Session, subject_id: int):
    return db.query(Subject).filter(Subject.id == subject_id).first()

async def get_subject_by_name(db: Session, subject_name: str):
    return db.query(Subject).filter(Subject.subject_name == subject_name).first()

async def create_subject(db: Session, subject: schema.CreateSubject,teacher_id: int):
    new_subject = Subject(
        subject_name=subject.subject_name,
        major=subject.major,
        level=subject.level,
        start_year=subject.start_year,
        semester=subject.semester,
        is_active=True,
        teacher_id=teacher_id
    )

    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

async def create_enrollment(db: Session, subject_id:int, student_id:int):
    new_enrollment = Enrollment(
        student_id=student_id,
        subject_id=subject_id,
        feedback=False,
        is_active=True
    )

    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment

async def get_enrollment_by_and_subject_id(db: Session,subject_id: int) -> List[int]:
    return [enrollments.student_id for enrollments in db.query(Enrollment).filter(Enrollment.subject_id == subject_id).all()]