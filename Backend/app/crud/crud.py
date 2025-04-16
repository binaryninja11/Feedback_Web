from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.models.dbmodel import Student, Teacher, Subject, Enrollment, Question, Feedback
from app.schemas import schema
from app.task import task
from fastapi import HTTPException

from sqlalchemy.orm import aliased
from sqlalchemy.sql import label



async def create_student(db: Session, student: schema.SignUpStudent):
    if db.query(Student).filter(Student.stdid == student.stdid).first():
        raise HTTPException(status_code=400, detail="Student already registered")

    new_student = Student(
        stdid=student.stdid,
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

async def get_subjects_by_level_and_major(db: Session, level: int, major: str) -> List[int]:
    return [subject.id for subject in db.query(Subject).filter(Subject.level == level, Subject.major == major).all()]
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


async def create_enrollments(db: Session, stId: int, subject_ids: List[int]):
    try:
        # Create a list of Enrollment objects
        new_enrollments = [
            Enrollment(
                student_id=stId,
                subject_id=subject_id,
                feedback=False,
                is_active=True
            )
            for subject_id in subject_ids
        ]

        # Add all enrollments to the session
        db.add_all(new_enrollments)

        # Commit the session to persist changes
        db.commit()

        # Refresh each individual Enrollment object
        for enrollment in new_enrollments:
            db.refresh(enrollment)

        return new_enrollments

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


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

async def get_questions_with_active(db: Session) -> List[schema.ResponseQuestionWithActive]:
    result = db.execute(
        select(
            Question.id,
            Question.header,
            Question.body,
            Question.requirement,
            Question.type,
        )
        .filter(Question.is_active == True)
        .order_by(Question.order)
    )

    questions = result.mappings().all()

    return [schema.ResponseQuestionWithActive(**question) for question in questions]

async def get_questions(db: Session) -> List[schema.ResponseQuestion]:
    result = db.execute(
        select(
            Question.id,
            Question.order,
            Question.header,
            Question.body,
            Question.requirement,
            Question.type,
            Question.is_active
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

        subject_id: int
):
    new_feedback = Feedback(
        question_id=feedback.question_id,
        answer=feedback.answer,
        is_active=True,
        subject_id=subject_id
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

# multiple feedbacks
async def create_student_feedbacks(
        db: Session,
        feedbacks: list[schema.create_feedback_with_qtype],
        subject_id: int
):
    if not feedbacks:
        raise HTTPException(status_code=400, detail="No feedbacks provided")

    new_feedbacks = [
        Feedback(
            question_id=feedback.question_id,
            answer=feedback.answer,
            is_active=True,
            subject_id=subject_id,
            qestion_type=feedback.type
        )
        for feedback in feedbacks
    ]

    db.add_all(new_feedbacks)
    db.commit()

    return new_feedbacks

async def enrollment_feedback_true(
        db: Session,
        student_id: int,
        subject_id: int
):
    enrollment = db.query(Enrollment).filter(Enrollment.student_id == student_id, Enrollment.subject_id == subject_id).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    enrollment.feedback = True
    db.commit()
    db.refresh(enrollment)

    return "successfully updated feedback to true"

# Delete all enrollments (New Semester)
async def new_semester(db: Session):
    try:
        db.query(Enrollment).delete(synchronize_session="fetch")
        db.commit()
        return "Successfully updated semester"
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# Update all student levels (New Academic Year)
async def UpdateStudentLevel(db: Session):
    try:
        db.query(Student).update({Student.level: Student.level + 1}, synchronize_session="fetch")
        db.query(Enrollment).delete(synchronize_session="fetch")
        db.commit()
        return "Successfully updated academic year"
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# get all teachers tid,name,last_name
async def get_all_teachers_tid_name_and_last(db: Session) -> List[schema.ResponseTeacher]:
    try:
        result = db.execute(
            select(
                Teacher.tid,
                Teacher.name,
                Teacher.last_name
            ).filter(Teacher.is_active == True)
        )

        teachers = result.mappings().all()

        return [schema.ResponseTeacher(**teacher) for teacher in teachers]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# get all subjects id,name
async def get_all_subjects_id_and_name(db: Session) -> List[schema.ResponseSujectIdName]:
    try:
        result = db.execute(
            select(
                Subject.id.label("subject_id"),
                Subject.subject_name
            ).filter(Subject.is_active == True)
        )

        subjects = result.mappings().all()

        return [schema.ResponseSujectIdName(**subject) for subject in subjects]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# In crud.py or wherever your logic is
async def archive_question_by_id(db: Session, question_id: int,action: bool):
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        question.is_active = action
        db.commit()
        db.refresh(question)
        return "Question archived successfully"
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error: " + str(e))

# get the subject_id answer question_type True from enrolment
from sqlalchemy import func, case

async def get_subject_id_answer_question_type_true(db: Session) -> dict:
    try:
        result = db.execute(
            select(
                Feedback.subject_id,
                func.count(case((Feedback.answer == "Excellent", 1))).label("excellent"),
                func.count(case((Feedback.answer == "Very Good", 1))).label("very_Good"),
                func.count(case((Feedback.answer == "Good", 1))).label("good"),
                func.count(case((Feedback.answer == "Fair", 1))).label("fair"),
                func.count(case((Feedback.answer == "Poor", 1))).label("poor"),
                func.count(case((Feedback.answer == "Very Poor", 1))).label("very_Poor"),
            )
            .where(
                Feedback.qestion_type == True
            )
            .group_by(Feedback.subject_id)
        )

        feedbacks = result.mappings().all()

        dicts = {}
        for row in feedbacks:
            dicts[row.subject_id] = {
                "excellent": row.excellent,
                "very_Good": row.very_Good,
                "good": row.good,
                "fair": row.fair,
                "poor": row.poor,
                "very_Poor": row.very_Poor
            }

        return dicts

    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error: " + str(e))

async def get_all_teachers_id_subject_id(db: Session) -> List[schema.Teacher_id_subject_id]:
    try:
        result = db.execute(
            select(
                Teacher.id.label("teacher_id"),
                Teacher.name.label("teacher_name"),
                func.array_agg(Subject.id).label("subject_ids")
            )
            .join(Subject, Subject.teacher_id == Teacher.id)
            .group_by(Teacher.id)
        )

        rows = result.mappings().all()

        return [schema.Teacher_id_subject_id(**row) for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error: " + str(e))

async def get_subject_feedback(db: Session, subject_id: int) -> schema.SubjectDetail:
    try:
        subject = await get_subject_by_id(db=db, subject_id=subject_id)
        if not subject:
            raise HTTPException(status_code=400, detail="Subject not found")
        teacher = await get_teacher_by_id(db=db, teacher_id=subject.teacher_id)

        result = db.execute(
            select(
                func.count(case((Feedback.answer == "Excellent", 1))).label("excellent"),
                func.count(case((Feedback.answer == "Very Good", 1))).label("very_Good"),
                func.count(case((Feedback.answer == "Good", 1))).label("good"),
                func.count(case((Feedback.answer == "Fair", 1))).label("fair"),
                func.count(case((Feedback.answer == "Poor", 1))).label("poor"),
                func.count(case((Feedback.answer == "Very Poor", 1))).label("very_Poor"),
            )
            .where(Feedback.subject_id == subject_id)
            .group_by(Feedback.subject_id)
        )

        row = result.mappings().first()

        if not row:
            row = {
                "excellent": 0, "very_Good": 0, "good": 0,
                "fair": 0, "poor": 0, "very_Poor": 0
            }

        total = (
            row["excellent"] + row["very_Good"] + row["good"] +
            row["fair"] + row["poor"] + row["very_Poor"]
        )

        if total == 0:
            average = 0.0
        else:
            sum_score = (
                row["excellent"] * 10 +
                row["very_Good"] * 9 +
                row["good"] * 7 +
                row["fair"] * 5 +
                row["poor"] * 3 +
                row["very_Poor"] * 1
            )
            average = round(sum_score / total, 2)
            label = task.get_rating_label(average)

        return schema.SubjectDetail(
            subject_id=subject.id,
            teacher_name=f"{teacher.name} {teacher.last_name}",
            subject_name=subject.subject_name,
            major=subject.major,
            level=subject.level,
            start_year=subject.start_year,
            semester=subject.semester,
            feedback=schema.FeedbackName(**row),
            avarage=label
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error: " + str(e))

def get_subjects_by_filter(db: Session, filter: schema.GetFilterBody,teacherId:int = None):
    try:
        query = db.query(Subject).filter(Subject.is_active == True)

        if filter.level is not None:
            query = query.filter(Subject.level == filter.level)
        if filter.major is not None:
            query = query.filter(Subject.major == filter.major)
        if filter.semester is not None:
            query = query.filter(Subject.semester == filter.semester)
        if filter.teacherId is not None:
            query = query.filter(Subject.teacher_id == teacherId)

        return query.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error: " + str(e))


