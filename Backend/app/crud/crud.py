from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.models.dbmodel import Student, Teacher, Subject, Enrollment, Question, Feedback
from app.schemas import schema
from fastapi import HTTPException

from sqlalchemy.orm import aliased
from sqlalchemy.sql import label


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

async def get_enrollment_by_student_id(db: Session, student_id: int) -> List[int]:
    return [enrollments.subject_id for enrollments in db.query(Enrollment).filter(Enrollment.student_id == student_id).all()]

async def get_enrollment_subjects_by_student_id(db: Session, student_id: int) -> List[schema.EnrollmentStudentSubjects]:
    result = db.execute(
        select(
            Enrollment.subject_id,
            Subject.subject_name,
            Enrollment.feedback
        )
        .join(Subject, Enrollment.subject_id == Subject.id)
        .filter(Enrollment.student_id == student_id, Subject.is_active == True)
    )

    subjects = result.mappings().all()

    return [schema.EnrollmentStudentSubjects(**subject) for subject in subjects]

async def get_enrollment_by_student_and_subject(db: Session, student_id: int, subject_id: int):
    return db.query(Enrollment).filter(Enrollment.student_id == student_id, Enrollment.subject_id == subject_id).first()

async def get_last_order_in_questions(db: Session) -> int:
    last_order = db.query(func.max(Question.order)).scalar()
    return last_order if last_order is not None else 0

async def create_question(db: Session, question: schema.CreateQuestion,order: int):
    new_question = Question(
        order=order,
        header=question.header,
        body=question.body,
        requirement=question.requirement,
        type=question.type,
        is_active=True
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

async def get_question_by_id(db: Session, question_id: int):
    return db.query(Question).filter(Question.id == question_id).first()

async def get_questions(db: Session) -> List[schema.ResponseQuestion]:
    result = db.execute(
        select(
            Question.id,
            Question.order,
            Question.header,
            Question.body,
            Question.requirement,
            Question.type
        )
        .order_by(Question.order)
    )

    questions = result.mappings().all()

    return [schema.ResponseQuestion(**question) for question in questions]

async def delete_question(db: Session, question_id: int):
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:  # Check if the question exists before deleting
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()

    return "Deleted successfully"

async def order_update_questions(db: Session, question_id_order_one: int, question_id_order_two: int):
    question1 = db.query(Question).filter(Question.id == question_id_order_one).first()
    question2 = db.query(Question).filter(Question.id == question_id_order_two).first()

    if not question1 or not question2:
        raise HTTPException(status_code=404, detail="One or both questions not found")

    # Swap the order
    question1.order, question2.order = question2.order, question1.order

    db.commit()
    db.refresh(question1)
    db.refresh(question2)

    return "Order updated successfully"

async def get_count_questions(db: Session) -> int:
    count = db.query(Question).count()
    return count



async def get_requrtmen_question_id(db: Session) -> List[int]:
    return [questions.id for questions in db.query(Question).filter(Question.requirement == True).all()]


async def create_student_feedback(
        db: Session,
        feedback: schema.post_student_feedback,
        student_id: int,
        subject_id: int
):
    new_feedback = Feedback(
        question_id=feedback.question_id,
        answer=feedback.answer,
        is_active=True,
        student_id=student_id,
        subject_id=subject_id
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

# multiple feedbacks
async def create_student_feedbacks(
        db: Session,
        feedback: list[schema.post_student_feedback],
        student_id: int,
        subject_id: int
):
    return ...