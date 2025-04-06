from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.schema import Token, TokenData, Student
from app.crud.crud import get_student_by_stdid
from app.dependencies import get_db
from app.utils import utils as auth_utils

router = APIRouter(prefix="/auth", tags=["auth"])

# # Load environment variables
# load_dotenv()
#
# SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
# ALGORITHM = os.getenv("ALGORITHM", "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
#

#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/signin")
#
#
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify if the plain password matches the hashed password."""
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password: str) -> str:
#     """Hash the password using bcrypt."""
#     return pwd_context.hash(password)
#
#
# def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
#     """Create a JWT access token with an expiration time."""
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#
#
# async def authenticate_user(db: Session, stdid: str, password: str):
#     """Authenticate user by checking credentials against the database."""
#     student = get_student_by_stdid(db, stdid)
#
#     if not student or not verify_password(password, student.hashed_password):
#         return None
#     return student
#
#
# async def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
#     """Retrieve the current authenticated user from the JWT token."""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         if datetime.fromtimestamp(payload["exp"], tz=timezone.utc) < datetime.now(timezone.utc):
#             raise HTTPException(status_code=401, detail="Token expired")
#         user = get_student_by_stdid(db, payload["sub"])
#         if user is None:
#             raise credentials_exception
#         return user
#     except (InvalidTokenError, ExpiredSignatureError):
#         raise credentials_exception


@router.post("/signin", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    # try:
        """Login endpoint to generate a JWT token for authenticated users."""
        student = await auth_utils.authenticate_user(db, form_data.username, form_data.password)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect student ID or password",
                headers={"WWW-Authenticate": "Bearer"},
            )


        access_token = await auth_utils.create_access_token(data={"sub": student.stdid})

        return Token(access_token=access_token, token_type="bearer")

    # except HTTPException as http_exc:
    #     print("http_exc", http_exc)
    #     raise http_exc
    # except SQLAlchemyError as e:
    #     raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Server error {str(e)}")


@router.get("/student/me", response_model=Student)
async def read_users_me(current_user: Annotated[Student, Depends(auth_utils.get_current_user)]):
    """Retrieve details of the currently authenticated student."""
    return current_user


