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

# # ✅ post_subject
# @router.post("/subject", response_model=schema.Student)

