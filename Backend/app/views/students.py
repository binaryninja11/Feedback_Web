from typing import List

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import schema
from app.crud import crud



from app.utils import utils as auth_utils

router = APIRouter(prefix='/students', tags=["students"])


# ✅ create_student
@router.post("", response_model=schema.Student)
async def create_student(student: schema.SignUpStudent, db: Session = Depends(get_db)):
    try:

        student.password = auth_utils.pwd_context.hash(student.password)
        st = await crud.create_student(db=db, student=student)

        # add student to the subjects
        # get all subjects with students level and major
        subject_ids = await crud.get_subjects_by_level_and_major(db=db, level=student.level, major=student.major)
        if not subject_ids:
            raise HTTPException(status_code=200, detail="student created but No subjects found for this student")

        # create enrollment
        enrollment = await crud.create_enrollments(db=db, stId=st.id, subject_ids=subject_ids)
        if not enrollment:
            raise HTTPException(status_code=200, detail="student created but No subjects found for this student")

        return st

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

# ✅ get_enrollment_subjects
@router.get("/enrollment/subjects", response_model=List[schema.EnrollmentStudentSubjects])
async def get_enrollment_subjects(
    current_user: schema.Student = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check if the student exists
        student = await crud.get_student_by_id(db=db, student_id=current_user.id)
        if not student:
            raise HTTPException(status_code=400, detail="Student not found")

        # Get enrolled subjects
        subjects = await crud.get_enrollment_subjects_by_student_id(db=db, student_id=current_user.id)

        if not subjects:
            raise HTTPException(status_code=400, detail="No subjects found for this student")

        return subjects

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

# ✅ get_questions
@router.get("/questions", response_model=List[schema.ResponseQuestionWithActive])
async def get_question(
    current_user: schema.Student = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    try:

        # Get questions
        questions = await crud.get_questions_with_active(db=db)

        if not questions:
            raise HTTPException(status_code=400, detail="No questions found for this student")

        return questions

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}"
)

# ✅ post_student_feedback
@router.post("/feedback/{subject_id}")
async def post_student_feedback(
    subject_id: int ,
    feedbacks: list[schema.post_student_feedback] = Body(...),
    current_user: schema.Student = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check if the subject exists
        subject = await crud.get_subject_by_id(db=db, subject_id=subject_id)
        if not subject:
            raise HTTPException(status_code=400, detail="Subject not found")


        # Check if the student is enrolled in the subject
        enrollment = await crud.get_enrollment_by_student_and_subject(db=db, student_id=current_user.id,subject_id=subject_id)
        if not enrollment:
            raise HTTPException(status_code=400, detail="Student is not enrolled in this subject")

        # Check if the student give feedback for the subject
        if enrollment.feedback == True:
            raise HTTPException(status_code=400, detail="Student has already given feedback for this subject")

        # get all required questions ids
        required_questions_ids = await crud.get_requrtmen_question_id(db=db)

        feedbaks_with_qtype = []

        for feedback in feedbacks:
            question_type = False
            # Check if the question exists
            question = await crud.get_question_by_id(db=db, question_id=feedback.question_id)
            if not question:
                raise HTTPException(status_code=400, detail="Question not found")

            # Check if the answer is valid for Multiple Choice questions
            if question.type == schema.QuestionType.multiple:
                if feedback.answer not in {choice.value for choice in schema.MultipleChoiceQuestion}:
                    raise HTTPException(status_code=400, detail="Invalid answer for Multiple Choice question")

                question_type = True

            # Check if the question is required
            if question.id in required_questions_ids:
                # Check if the feedback is empty
                if not feedback.answer:
                    raise HTTPException(status_code=400, detail="Feedback cannot be empty for required questions")
                # remuve id from required_questions_ids
                required_questions_ids.remove(question.id)

            # Append the feedback with question type
            feedbaks_with_qtype.append(schema.create_feedback_with_qtype(
                question_id=feedback.question_id,
                answer=feedback.answer,
                type = question_type
            ))


        # Check if all required questions have been answered
        if len(required_questions_ids) != 0:
            raise HTTPException(status_code=400, detail="Feedback cannot be empty for required questions")


        # creates feedbacks
        feedbaks = await crud.create_student_feedbacks(db=db,
                                                       feedbacks=feedbaks_with_qtype,
                                                       subject_id=subject_id)

        # enrrolment feed bak true
        enrollment_to_true = await crud.enrollment_feedback_true(db=db,
                                                     student_id=current_user.id,
                                                     subject_id=subject_id)


        return "successfully created feedbacks for the subject"

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")
