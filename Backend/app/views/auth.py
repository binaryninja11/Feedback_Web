# pip install pyjwt
# pip install "passlib[bcrypt]"

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends,  HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas import schema
from app.crud import crud

from app.dependencies import get_db

# Load environment variables
load_dotenv()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "SECRET_KEY"
ALGORITHM = "ALGORITHM"
ACCESS_TOKEN_EXPIRE_MINUTES = "ACCESS_TOKEN_EXPIRE_MINUTES"

router = APIRouter(prefix='/auth', tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    stdid: str | None = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db, stdid: str, password: str):
    st = crud.get_student_by_stdid(db=db, student_id=stdid)
    if not st:
        return False
    if not verify_password(password, st.hashed_password):
        return False
    return st


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        stdid = payload.get("sub")
        if stdid is None:
            raise credentials_exception
        token_data = TokenData(stdid=stdid)
    except InvalidTokenError:
        raise credentials_exception
    user = await crud.get_student_by_stdid(db,token_data.stdid)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[schema.Student, Depends(get_current_user)],
):
    if current_user.active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup (
        student: schema.SignUpStudent,
        db: Session = Depends(get_db)
):
    try:
        student.password = get_password_hash(student.password)
        new_student = await crud.create_student(db, student)

        return new_student

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error {str(e)}")


@router.post("/signin", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    student:schema.Student = authenticate_user(db, form_data.stdid, form_data.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": student.stdid}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/student/me/", response_model=schema.Student)
async def read_users_me(
    current_user: Annotated[schema.Student, Depends(get_current_active_user)],
):
    return current_user
