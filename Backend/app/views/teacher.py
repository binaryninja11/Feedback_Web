from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import schema
from app.crud import crud

from starlette.concurrency import run_in_threadpool

from app.utils import utils as auth_utils

router = APIRouter(prefix='/teacher', tags=["teacher"])


# ✅ create_teacher
@router.post("", response_model=schema.Teacher)
async def create_student(teacher: schema.SignUpTeacher, db: Session = Depends(get_db)):
    try:

        teacher.password = auth_utils.pwd_context.hash(teacher.password)
        tt = await crud.create_teacher(db=db, teacher=teacher)

        return tt

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")



