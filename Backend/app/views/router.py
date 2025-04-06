from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import schema
from app.crud import categorycrud as crud

from starlette.concurrency import run_in_threadpool



router = APIRouter(prefix='/category', tags=["Category"])


# ✅ Get image by id +
@router.get("/image/{image_id}", response_model=schema.Image)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    try:
        image = await run_in_threadpool(crud.get_image_by_id, db, image_id)
        if not image:
            raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
        return image

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")
