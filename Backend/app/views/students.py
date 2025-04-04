from typing import List

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import schema
from app.crud import crud

from starlette.concurrency import run_in_threadpool

from app.utils import utils as auth_utils

router = APIRouter(prefix='/students', tags=["students"])


# ✅ create_student
@router.post("", response_model=schema.Student)
async def create_student(student: schema.SignUpStudent, db: Session = Depends(get_db)):
    try:

        student.password = auth_utils.pwd_context.hash(student.password)
        st = await crud.create_student(db=db, student=student)

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
@router.get("/questions", response_model=List[schema.ResponseQuestion])
async def get_question(
    current_user: schema.Student = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    try:

        # Get questions
        questions = await crud.get_questions(db=db)

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
    feedbacks: list[schema.post_student_feedback],
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

        # get all required questions ids
        required_questions_ids = await crud.get_requrtmen_question_id(db=db)

        for feedback in feedbacks:
            # Check if the question exists
            question = await crud.get_question_by_id(db=db, question_id=feedback.question_id)
            if not question:
                raise HTTPException(status_code=400, detail="Question not found")

            # Check if the question is of type "Multiple Choice"
            if question.type == schema.QuestionType.multiple:
                # Check if the answer is valid
                if feedback.answer not in schema.MultipleChoiceQuestion:
                    raise HTTPException(status_code=400, detail="Invalid answer for Multiple Choice question")

            # Check if the question is required
            if question.id in required_questions_ids:
                # Check if the feedback is empty
                if not feedback.answer:
                    raise HTTPException(status_code=400, detail="Feedback cannot be empty for required questions")
                # remuve id from required_questions_ids
                required_questions_ids.remove(question.id)

        # Check if all required questions have been answered
        if len(required_questions_ids) != 0:
            raise HTTPException(status_code=400, detail="Feedback cannot be empty for required questions")


        # creates feedbacks

        feedbaks = await crud.create_student_feedbacks(db=db,
                                                       feedbacks=feedbacks,
                                                       student_id=current_user.id,
                                                       subject_id=subject_id)

        return feedback

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")
