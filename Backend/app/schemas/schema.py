from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class Major(str, Enum):
    se = "Software Engineering"
    bm = "Business Management"
    it = "Information Technology"
    ad = "Art and Design"
    me = "Mechanical Engineering"


class SignUpStudent(BaseModel):
    stdid: str
    name: str
    last_name: str
    password: str
    level: str in [1,2,3,4]
    major: Major

class CreateStudent(BaseModel):
    stdid: str
    name: str
    last_name: str
    password: str
    level: str
    major: Major
    active: bool = True

class Student(BaseModel):
    id: int
    stdid: str
    name: str
    last_name: str
    level: str
    major: Major
    active: bool

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    stdid: str = None
    name: str = None
    last_name: str = None
    level: str = None
    major: str = None

    class Config:
        from_attributes = True


