from datetime import datetime, timedelta, timezone
from typing import Annotated, List

import jwt
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas import schema
from app.crud import crud
from app.schemas.schema import Token, TokenData, Student
from app.crud.crud import get_student_by_stdid
from app.dependencies import get_db

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

router = APIRouter(prefix="/admin", tags=["admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/admin/signin")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash the password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class Admin(BaseModel):
    username: str
    password: str

admin_db = {
    "admin": Admin(username="admin", password=get_password_hash("admin"))
}

async def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user by checking credentials against the database."""
    try:
        admin = admin_db[username]
    except KeyError:
        admin = None

    if not admin or not verify_password(password, admin.password):
        return None
    return admin




async def get_current_user(token: str = Depends(oauth2_bearer)):
    """Retrieve the current authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(payload["exp"], tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")
        admin = admin_db[payload["sub"]]
        if admin is None:
            raise credentials_exception
        return admin
    except (InvalidTokenError, ExpiredSignatureError):
        raise credentials_exception


@router.post("/signin", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    # try:
        """Login endpoint to generate a JWT token for authenticated users."""
        admin = await authenticate_user(db, form_data.username, form_data.password)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect student ID or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": admin.username}, expires_delta=access_token_expires)

        return Token(access_token=access_token, token_type="bearer")

@router.get("/me")
async def read_users_me(current_user: Annotated[Student, Depends(get_current_user)]):
    return current_user

#  get all teachers tid , name nad lastname
@router.get("/teachers", response_model=List[schema.ResponseTeacher])
async def get_all_teachers(
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        teachers = await crud.get_all_teachers_tid_name_and_last(db=db)

        if not teachers:
            raise HTTPException(status_code=404, detail="No teachers found")

        return teachers

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

#  get all subjects id and name
@router.get("/subjects", response_model=List[schema.ResponseSujectIdName])
async def get_all_subjects(
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        subjects = await crud.get_all_subjects_id_and_name(db=db)

        if not subjects:
            raise HTTPException(status_code=404, detail="No subjects found")

        return subjects

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

# Create a new subject
@router.post("/subject")
async def create_new_subjects(
    subject: schema.CreateSubject,
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        # Check if the subject already exists
        subject_exists = await crud.get_subject_by_name(db=db, subject_name=subject.subject_name)

        if subject_exists:
            raise HTTPException(status_code=400, detail="Subject already exists")

        # Check if the teacher exists
        teacher = await crud.get_teacher_by_tid(db=db, teacher_tid=subject.teacher_tid)

        if not teacher:
            raise HTTPException(status_code=400, detail="Teacher not found")

        # Create the subject
        new_subject = await crud.create_subject(db=db, subject=subject, teacher_id=teacher.id)

        return "Subject created successfully"

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

# Add student to subject by student stdid
@router.post("/subject/add_student")
async def add_student_to_subject(
    enroll: schema.CreateEnrollment,
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        # Check if the subject exists
        subject = await crud.get_subject_by_id(db=db, subject_id=enroll.subject_id)

        if not subject:
            raise HTTPException(status_code=400, detail="Subject not found")

        # Check if the student exists
        student = await crud.get_student_by_stdid(db=db, stdid=enroll.stdid)

        if not student:
            raise HTTPException(status_code=400, detail="Student not found")

        # Add student to subject
        await crud.create_enrollment(db=db, subject_id=enroll.subject_id, student_id=student.id)

        return "Student added to subject successfully"

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")


# Add students to subject
@router.post("/subject/add_students")
async def add_students_to_subject(
        enrollments: schema.CreateEnrollments,
        current_user: Annotated[Student, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        # Check if the subject exists
        subject = await crud.get_subject_by_id(db=db, subject_id=enrollments.subject_id)

        if not subject:
            raise HTTPException(status_code=400, detail="Subject not found")

        student_ids = await crud.get_student_by_level_and_major(db=db, level=enrollments.level, major=enrollments.major)
        enrolled_students = await crud.get_enrollment_by_and_subject_id(db=db,subject_id=enrollments.subject_id)

        student_ids = [student_id for student_id in student_ids if student_id not in enrolled_students]

        for student_id in student_ids:
            await crud.create_enrollment(db=db, subject_id=enrollments.subject_id, student_id=student_id)

        return "Students added to subject successfully"

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

# get all questions
@router.get("/questions", response_model=List[schema.ResponseQuestion])
async def get_questions(
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        questions = await crud.get_questions(db=db)

        if not questions:
            raise HTTPException(status_code=404, detail="No questions found")

        return questions

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

# create new question
@router.post("/question")
async def create_new_question(
    question: schema.CreateQuestion,
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        order = await crud.get_last_order_in_questions(db=db)

        # Create the question
        new_question = await crud.create_question(db=db, question=question,order=order+1)

        return "Question created successfully"

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

# delete question
@router.delete("/question/{question_id}")
async def delete_question(
    question_id: int,
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        # Check if the question exists
        question = await crud.get_question_by_id(db=db, question_id=question_id)

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        # Delete the question
        await crud.delete_question(db=db, question_id=question_id)

        return "Question deleted successfully"

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")

# replace question order
@router.put("/question/order")
async def replace_question_order(
    question: schema.ChangeQuestionOrder,
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        # Check if the questions exist
        question1 = await crud.get_question_by_id(db=db, question_id=question.question_id_order_one)
        question2 = await crud.get_question_by_id(db=db, question_id=question.question_id_order_two)

        if not question1 or not question2:
            raise HTTPException(status_code=404, detail="One or both questions not found")

        # Swap the order
        await crud.order_update_questions(db=db, question_id_order_one=question.question_id_order_one, question_id_order_two=question.question_id_order_two)

        return "Question order replaced successfully"

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")


# New academic year or semester API route
@router.post("/newacademic")
async def create_new_academic_year_or_semester(
    academic_year: schema.CreateAcademicYear,
    current_user: Annotated[Student, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        if current_user.username != "admin":
            raise HTTPException(status_code=401, detail="Unauthorized access")

        if academic_year.aos.value == schema.AcademicYearOrSemester.semester.value:
            return await crud.new_semester(db=db)

        elif academic_year.aos.value == schema.AcademicYearOrSemester.academic_year.value:
            return await crud.UpdateStudentLevel(db=db)

        raise HTTPException(status_code=400, detail="Invalid type, use 'semester' or 'academic'")

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")



